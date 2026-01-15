from otree.api import *

doc = """
Part 4: Survey.
"""

class Constants(BaseConstants):
    name_in_url = 'app_survey'
    players_per_group = None
    num_rounds = 1

# 定义通用的 1-7 量表列表
LIKERT_7 = [1, 2, 3, 4, 5, 6, 7]

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # --- 1. Experience (Feedback Part 1) ---
    exp1 = models.IntegerField(choices=LIKERT_7, label="1.", widget=widgets.RadioSelectHorizontal)
    exp2 = models.IntegerField(choices=LIKERT_7, label="2.", widget=widgets.RadioSelectHorizontal)
    
    # --- 2. Situational Empathy (Feedback Part 2) ---
    ses1 = models.IntegerField(
        choices=LIKERT_7, widget=widgets.RadioSelectHorizontal,
        label="1. After the 10-minute conversation I just had, I feel that if I were to see someone in trouble right now, I would really want to help them."
    )
    ses2 = models.IntegerField(
        choices=LIKERT_7, widget=widgets.RadioSelectHorizontal,
        label="2. The 10-minute conversation makes me feel that I am now more likely to have compassionate and concerned feelings for others' misfortunes."
    )
    ses3 = models.IntegerField(
        choices=LIKERT_7, widget=widgets.RadioSelectHorizontal,
        label='3. Right now, I feel more like a "soft-hearted" person than I usually do.'
    )
    ses4 = models.IntegerField(
        choices=LIKERT_7, widget=widgets.RadioSelectHorizontal,
        label="4. After the 10-minute conversation I just had, I feel that if I were in a disagreement with someone, I would be more willing to try to understand their point of view."
    )
    ses5 = models.IntegerField(
        choices=LIKERT_7, widget=widgets.RadioSelectHorizontal,
        label='5. The 10-minute conversation has inspired me, making me feel that it is now easier to "put myself in other people\'s shoes."'
    )
    ses6 = models.IntegerField(
        choices=LIKERT_7, widget=widgets.RadioSelectHorizontal,
        label="6. Right now, I believe that taking the time to understand other people's perspectives is very valuable."
    )
    
    # --- 3. Decision Factors (Review of Tasks) ---
    f1 = models.IntegerField(
        choices=LIKERT_7, widget=widgets.RadioSelectHorizontal,
        label="1. When making decisions in the money allocation tasks, I cared about how much the person paired with me could earn and how he/she would feel about the outcome."
    )
    f2 = models.IntegerField(
        choices=LIKERT_7, widget=widgets.RadioSelectHorizontal,
        label="2. The good mood I was in after the 10-minute conversation made me behave more generously in the money allocation tasks."
    )
    f3 = models.IntegerField(
        choices=LIKERT_7, widget=widgets.RadioSelectHorizontal,
        label="3. I wanted to behave generously in the money allocation tasks because it would make me feel like I am a good person."
    )
    f4 = models.IntegerField(
        choices=LIKERT_7, widget=widgets.RadioSelectHorizontal,
        label="4. I wanted to behave generously in the money allocation tasks because it would allow me to present a positive social image to my partner or to the researchers."
    )
    
    # --- 4. Other (Final Question & Demographics) ---
    human_likeness = models.IntegerField(choices=LIKERT_7, label="To what extent did you feel you were talking to a real human?", widget=widgets.RadioSelectHorizontal)
    
    # 【已修改】恢复为 18 岁及以上
    age = models.IntegerField(min=18, max=100, label="Age")
    
    gender = models.StringField(choices=["Male", "Female", "Non-binary", "Prefer not to say"], label="Gender")
    nationality = models.StringField(label="Nationality")
    ai_use_freq = models.StringField(choices=["Rarely", "Occasionally", "Frequently", "Daily"], label="AI Usage Frequency")
    used_companion = models.StringField(choices=["No", "Yes"], label="Used AI Companion?")
    
    final_payoff_usd = models.CurrencyField()

# --- Pages ---

class Experience(Page):
    form_model = 'player'
    form_fields = ['exp1', 'exp2']
    @staticmethod
    def is_displayed(player): return not player.participant.vars.get('terminate', False)
    
    @staticmethod
    def vars_for_template(player):
        role = player.participant.vars.get('chat_role', 'Sharer')
        q1_text = "I felt successful putting myself in my partner's shoes." if role == "Listener" else "I felt my partner put themselves in my shoes."
        q2_text = "I felt emotionally engaged in the conversation." if role == "Listener" else "I felt heard and understood by my partner."
        return dict(q1=q1_text, q2=q2_text)

class SituationalEmpathy(Page):
    form_model = 'player'
    form_fields = ['ses1', 'ses2', 'ses3', 'ses4', 'ses5', 'ses6']
    @staticmethod
    def is_displayed(player): return not player.participant.vars.get('terminate', False)

class DecisionFactors(Page):
    form_model = 'player'
    form_fields = ['f1', 'f2', 'f3', 'f4']
    @staticmethod
    def is_displayed(player): return not player.participant.vars.get('terminate', False)

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'nationality', 'ai_use_freq', 'used_companion']
    @staticmethod
    def is_displayed(player): return not player.participant.vars.get('terminate', False)

class HumanLikeness(Page):
    form_model = 'player'
    form_fields = ['human_likeness']
    @staticmethod
    def is_displayed(player): return not player.participant.vars.get('terminate', False)

class Debrief(Page):
    @staticmethod
    def is_displayed(player): 
        return (not player.participant.vars.get('terminate', False)) and (player.participant.vars.get('condition') == "Group 2")

class Payoff(Page):
    @staticmethod
    def is_displayed(player): return not player.participant.vars.get('terminate', False)
    
    @staticmethod
    def vars_for_template(player):
        paid_task = player.participant.vars.get('paid_task', 'None')
        paid_tokens = player.participant.vars.get('paid_tokens', 0)
        
        # 获取详细解释文本
        explanation = player.participant.vars.get('payoff_explanation', '')
        
        total = player.participant.payoff_plus_participation_fee()
        player.final_payoff_usd = total
        usd_str = "{:.2f}".format(float(paid_tokens) * 0.05)
        
        return dict(
            paid_task=paid_task, 
            paid_tokens=paid_tokens, 
            paid_usd=usd_str, 
            total_payoff=total,
            explanation=explanation
        )

page_sequence = [Experience, SituationalEmpathy, DecisionFactors, Demographics, HumanLikeness, Debrief, Payoff]