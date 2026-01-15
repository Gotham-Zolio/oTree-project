from otree.api import *
import random

doc = """
Part 1: Consent and Screening.
"""

class Constants(BaseConstants):
    name_in_url = 'app_intro'
    players_per_group = None
    num_rounds = 1

# 【修复】直接定义为列表，不要用函数
LIKERT_0_3 = [
    [0, "Not at all"], 
    [1, "Several days"], 
    [2, "More than half the days"], 
    [3, "Nearly every day"]
]

class Subsession(BaseSubsession):
    def creating_session(self):
        """在第一个 app 中进行分组，确保 participant.vars 在所有 app 中可用"""
        if self.round_number == 1:
            players = self.get_players()
            
            # 分配条件 (2:1:1:1)
            conditions = ["Group 1", "Group 1", "Group 2", "Group 3", "Group 4"]
            full_conditions = (conditions * (len(players)//5 + 1))[:len(players)]
            random.shuffle(full_conditions)
            
            # 修正：确保 Group 1 的人数是偶数
            g1_indices = [i for i, c in enumerate(full_conditions) if c == "Group 1"]
            if len(g1_indices) % 2 != 0:
                full_conditions[g1_indices[-1]] = "Group 2"

            for p, cond in zip(players, full_conditions):
                p.participant.vars['condition'] = cond
                
                # 角色分配逻辑
                if cond == 'Group 1':
                    # 暂时标记，稍后在配对时确定具体是 Sharer 还是 Listener
                    p.participant.vars['chat_role'] = None
                else:
                    # AI 组都是 Sharer
                    p.participant.vars['chat_role'] = 'Sharer'
                
                # 分配后续游戏角色
                p.participant.vars['game_role_track'] = random.choice(['Track A', 'Track B'])
                if p.participant.vars['game_role_track'] == 'Track A':
                    p.participant.vars['trust_role'] = 'Sender'
                    p.participant.vars['ultimatum_role'] = 'Proposer'
                else:
                    p.participant.vars['trust_role'] = 'Receiver'
                    p.participant.vars['ultimatum_role'] = 'Responder'
            
            # 对 Group 1 进行配对并分配角色
            g1_players = [p for p in players if p.participant.vars['condition'] == 'Group 1']
            for i in range(0, len(g1_players), 2):
                if i+1 < len(g1_players):
                    roles = ['Sharer', 'Listener']
                    random.shuffle(roles)
                    g1_players[i].participant.vars['chat_role'] = roles[0]
                    g1_players[i+1].participant.vars['chat_role'] = roles[1]

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    consent = models.StringField(
        choices=[["agree", "Agree"], ["disagree", "Do not agree"]], 
        label="By clicking “Agree,” you indicate that you have read, understood, and voluntarily consent to participate in this study."
    )
    
    # 【修复】这里 choices 直接引用上面的列表变量
    phq1 = models.IntegerField(choices=LIKERT_0_3, label="1. Little interest or pleasure in doing things")
    phq2 = models.IntegerField(choices=LIKERT_0_3, label="2. Feeling down, depressed or hopeless")
    gad1 = models.IntegerField(choices=LIKERT_0_3, label="3. Feeling nervous, anxious or on edge")
    gad2 = models.IntegerField(choices=LIKERT_0_3, label="4. Not being able to stop or control worrying")
    phq9_suicide = models.IntegerField(choices=LIKERT_0_3, label="5. Thoughts that you would be better off dead or of hurting yourself in some way")
    
    diagnosed_disorder = models.StringField(choices=[["yes", "Yes"], ["no", "No"]], label="6. Have you ever been diagnosed with any mental disorders?")
    is_eligible = models.BooleanField(initial=True)

    def compute_ineligible(self):
        s_phq = (self.phq1 or 0) + (self.phq2 or 0)
        s_gad = (self.gad1 or 0) + (self.gad2 or 0)
        return (s_phq >= 3) or (s_gad >= 3) or ((self.phq9_suicide or 0) >= 1) or (self.diagnosed_disorder == "yes")

# --- Pages ---

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.consent != "agree":
            player.participant.vars['terminate'] = True

class Screening(Page):
    form_model = 'player'
    form_fields = ['phq1', 'phq2', 'gad1', 'gad2', 'phq9_suicide', 'diagnosed_disorder']

    @staticmethod
    def is_displayed(player):
        return player.consent == "agree" and not player.participant.vars.get('terminate', False)

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.compute_ineligible():
            player.participant.vars['terminate'] = True
            player.is_eligible = False
        else:
            player.is_eligible = True

class ScreenedOut(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('terminate', False) and player.consent == "agree"

class NotConsented(Page):
    @staticmethod
    def is_displayed(player):
        return player.consent == "disagree"

page_sequence = [Consent, Screening, ScreenedOut, NotConsented]