from otree.api import *
import random

doc = """
Part 3: Decision Tasks (Randomized Order + Role Binding).
"""

class Constants(BaseConstants):
    name_in_url = 'app_games'
    players_per_group = None
    num_rounds = 4 # 对应 4 个任务
    endowment = 100
    
    # Trust Game 参数
    trust_send_options = [0, 25, 50, 75, 100]
    trust_multiplier = 3
    trust_prediction_bonus = 10
    trust_prediction_error = 5
    
    # Risk Game 参数
    risk_sure = 40
    risk_wins = [68, 84, 108, 140]

TASKS = ['dictator', 'trust', 'ultimatum', 'risk']

class Subsession(BaseSubsession):
    def creating_session(self):
        """
        创建 Session 时运行的逻辑。
        """
        for p in self.get_players():
            # 这里的逻辑我们移到辅助函数 ensure_task_setup 里复用
            # 这样即使 creating_session 没跑好，后面也能补救
            ensure_task_setup(p)

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    current_task = models.StringField() # 记录这一轮做的是哪个任务

    # --- 1. Dictator Game ---
    dictator_sent = models.IntegerField(min=0, max=Constants.endowment)
    
    # --- 2. Trust Game ---
    trust_sent = models.IntegerField(choices=Constants.trust_send_options)
    trust_prediction = models.IntegerField(min=0, max=Constants.trust_multiplier * Constants.endowment)
    
    # Trust Receiver Strategy Method
    trust_return_25 = models.IntegerField(min=0, max=75)
    trust_return_50 = models.IntegerField(min=0, max=150)
    trust_return_75 = models.IntegerField(min=0, max=225)
    trust_return_100 = models.IntegerField(min=0, max=300)
    
    # --- 3. Ultimatum Game ---
    ultimatum_offer = models.IntegerField(min=0, max=Constants.endowment)
    ultimatum_mao = models.IntegerField(min=0, max=Constants.endowment)
    
    # --- 4. Risk Task ---
    risk_choice_1 = models.StringField(choices=['Option A', 'Option B'], widget=widgets.RadioSelectHorizontal)
    risk_choice_2 = models.StringField(choices=['Option A', 'Option B'], widget=widgets.RadioSelectHorizontal)
    risk_choice_3 = models.StringField(choices=['Option A', 'Option B'], widget=widgets.RadioSelectHorizontal)
    risk_choice_4 = models.StringField(choices=['Option A', 'Option B'], widget=widgets.RadioSelectHorizontal)

# --- 辅助函数：核心防崩逻辑 ---

def ensure_task_setup(player):
    """
    确保玩家的任务顺序、角色绑定都已经设置好。
    如果数据库里缺这些信息（比如旧Session），这里会现场补上。
    """
    participant = player.participant
    
    # 1. 初始化 Condition (Fallback)
    if 'condition' not in participant.vars:
        participant.vars['condition'] = 'Group 1'

    # 2. 角色绑定 (Role Binding) & 任务随机化 (Task Randomization)
    # 只需要生成一次，存在 participant.vars 里
    if 'game_role_track' not in participant.vars:
        # 随机分配轨道
        track = random.choice(['Track A', 'Track B'])
        participant.vars['game_role_track'] = track
        
        if track == 'Track A':
            participant.vars['trust_role'] = 'Sender'
            participant.vars['ultimatum_role'] = 'Proposer'
        else:
            participant.vars['trust_role'] = 'Receiver'
            participant.vars['ultimatum_role'] = 'Responder'

    if 'task_order' not in participant.vars:
        my_tasks = TASKS.copy()
        random.shuffle(my_tasks)
        participant.vars['task_order'] = my_tasks

    # 3. 将本轮任务写入 player.current_task (如果还没写的话)
    if not player.field_maybe_none('current_task'):
        task_order = participant.vars['task_order']
        # round_number 是 1-based, list 是 0-based
        current_task_index = (player.round_number - 1) % 4
        player.current_task = task_order[current_task_index]

# --- Pages ---

class IntroDecisionTasks(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and not player.participant.vars.get('terminate', False)

class ShuffleWaitPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and not player.participant.vars.get('terminate', False)
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        ensure_task_setup(player)

# --- Dictator Pages ---
class Dictator(Page):
    form_model = 'player'
    form_fields = ['dictator_sent']
    @staticmethod
    def is_displayed(player): 
        ensure_task_setup(player) # 防崩检查
        return player.current_task == 'dictator' and not player.participant.vars.get('terminate', False)

# --- Trust Pages ---
class TrustSenderDecision(Page):
    form_model = 'player'
    form_fields = ['trust_sent']
    @staticmethod
    def is_displayed(player):
        ensure_task_setup(player)
        return (player.current_task == 'trust' and 
                player.participant.vars.get('trust_role') == 'Sender' and 
                not player.participant.vars.get('terminate', False))

class TrustSenderPrediction(Page):
    form_model = 'player'
    form_fields = ['trust_prediction']
    @staticmethod
    def is_displayed(player):
        ensure_task_setup(player)
        return (player.current_task == 'trust' and 
                player.participant.vars.get('trust_role') == 'Sender' and 
                not player.participant.vars.get('terminate', False))
    @staticmethod
    def vars_for_template(player):
        sent = player.trust_sent
        if sent is None: sent = 0 
        return dict(sent=sent, tripled=sent * 3)

class TrustReceiverPlan(Page):
    form_model = 'player'
    form_fields = ['trust_return_25', 'trust_return_50', 'trust_return_75', 'trust_return_100']
    @staticmethod
    def is_displayed(player):
        ensure_task_setup(player)
        return (player.current_task == 'trust' and 
                player.participant.vars.get('trust_role') == 'Receiver' and 
                not player.participant.vars.get('terminate', False))

# --- Ultimatum Pages ---
class UltimatumProposer(Page):
    form_model = 'player'
    form_fields = ['ultimatum_offer']
    @staticmethod
    def is_displayed(player):
        ensure_task_setup(player)
        return (player.current_task == 'ultimatum' and 
                player.participant.vars.get('ultimatum_role') == 'Proposer' and 
                not player.participant.vars.get('terminate', False))

class UltimatumResponder(Page):
    form_model = 'player'
    form_fields = ['ultimatum_mao']
    @staticmethod
    def is_displayed(player):
        ensure_task_setup(player)
        return (player.current_task == 'ultimatum' and 
                player.participant.vars.get('ultimatum_role') == 'Responder' and 
                not player.participant.vars.get('terminate', False))

# --- Risk Pages ---
class Risk(Page):
    form_model = 'player'
    form_fields = ['risk_choice_1', 'risk_choice_2', 'risk_choice_3', 'risk_choice_4']
    @staticmethod
    def is_displayed(player): 
        ensure_task_setup(player)
        return player.current_task == 'risk' and not player.participant.vars.get('terminate', False)

# --- Final Calculation ---
class ComputePayoffsWaitPage(WaitPage):
    title_text = "Saving Decisions"
    body_text = "Please wait while the system loads the next part of the study."
    
    @staticmethod
    def is_displayed(player): 
        return player.round_number == Constants.num_rounds and not player.participant.vars.get('terminate', False)
    
    @staticmethod
    def after_all_players_arrive(group):
        subsession = group.subsession
        compute_final_payoffs(subsession)

# --- Payoff Calculation Logic ---

def compute_final_payoffs(subsession):
    players = subsession.get_players()
    
    # 1. 构建数据池 (Pool) - 从所有轮次收集
    pool_dictator = []
    pool_trust_sender = [] 
    pool_trust_receiver = [] 
    pool_ultimatum_proposer = [] 
    pool_ultimatum_responder = []
    
    for p in players:
        if p.participant.vars.get('terminate'): continue
        
        for prev_p in p.in_all_rounds():
            ensure_task_setup(prev_p) # 确保读取时有 task 信息
            task = prev_p.current_task
            
            if task == 'dictator' and prev_p.dictator_sent is not None:
                pool_dictator.append(prev_p.dictator_sent)
            
            if task == 'trust':
                role = p.participant.vars.get('trust_role')
                if role == 'Sender' and prev_p.trust_sent is not None:
                    pool_trust_sender.append((prev_p.trust_sent, prev_p.trust_prediction))
                elif role == 'Receiver' and prev_p.trust_return_25 is not None:
                    pool_trust_receiver.append((
                        prev_p.trust_return_25, prev_p.trust_return_50, 
                        prev_p.trust_return_75, prev_p.trust_return_100
                    ))
            
            if task == 'ultimatum':
                role = p.participant.vars.get('ultimatum_role')
                if role == 'Proposer' and prev_p.ultimatum_offer is not None:
                    pool_ultimatum_proposer.append(prev_p.ultimatum_offer)
                elif role == 'Responder' and prev_p.ultimatum_mao is not None:
                    pool_ultimatum_responder.append(prev_p.ultimatum_mao)

    # 2. 计算 Payoff
    for p in players:
        if p.participant.vars.get('terminate'): continue
        
        paid_task = random.choice(TASKS)
        payoff = 0
        explanation = ""
        
        target_round_player = None
        for prev_p in p.in_all_rounds():
            if prev_p.current_task == paid_task:
                target_round_player = prev_p
                break
        
        if not target_round_player:
            p.participant.vars['paid_task'] = "Error"
            p.participant.vars['paid_tokens'] = 0
            continue

        try:
            if paid_task == 'dictator':
                role = random.choice(['Sender', 'Receiver'])
                if role == 'Sender':
                    sent = target_round_player.dictator_sent
                    if sent is None: sent = 0
                    payoff = 100 - sent
                    explanation = f"You were selected as the <b>Sender</b>. You kept <b>{payoff}</b> tokens."
                else:
                    if pool_dictator:
                        received = random.choice(pool_dictator)
                        payoff = received
                        explanation = f"You were selected as the <b>Receiver</b>. The match sent you <b>{payoff}</b> tokens."
                    else:
                        payoff = 0
                        explanation = "Not enough participants to match."

            elif paid_task == 'trust':
                my_role = p.participant.vars.get('trust_role')
                if my_role == 'Sender':
                    my_sent = target_round_player.trust_sent
                    my_pred = target_round_player.trust_prediction
                    if my_sent is None: my_sent = 0
                    if my_pred is None: my_pred = 0
                    
                    if pool_trust_receiver:
                        r_plan = random.choice(pool_trust_receiver)
                        idx_map = {0:0, 25:0, 50:1, 75:2, 100:3}
                        if my_sent == 0:
                            returned = 0
                        else:
                            returned = r_plan[idx_map.get(my_sent, 0)]
                            
                        game_payoff = (100 - my_sent) + returned
                        bonus = 0
                        if abs(my_pred - returned) <= Constants.trust_prediction_error:
                            bonus = Constants.trust_prediction_bonus
                        payoff = game_payoff + bonus
                        explanation = f"You sent <b>{my_sent}</b>. The Receiver returned <b>{returned}</b>. Prediction Bonus: <b>{bonus}</b>. Total: <b>{payoff}</b>."
                    else:
                        payoff = 0
                        explanation = "Not enough receivers."
                else:
                    if pool_trust_sender:
                        s_data = random.choice(pool_trust_sender)
                        s_sent = s_data[0]
                        if s_sent is None: s_sent = 0
                        
                        if s_sent == 0:
                            payoff = 0
                            explanation = "Sender sent 0. You received 0."
                        else:
                            received = s_sent * 3
                            plan_map = {
                                25: target_round_player.trust_return_25,
                                50: target_round_player.trust_return_50,
                                75: target_round_player.trust_return_75,
                                100: target_round_player.trust_return_100
                            }
                            my_return = plan_map.get(s_sent, 0)
                            if my_return is None: my_return = 0
                            payoff = received - my_return
                            explanation = f"Sender sent <b>{s_sent}</b> (x3 = {received}). You returned <b>{my_return}</b>. You kept <b>{payoff}</b>."
                    else:
                        payoff = 0
                        explanation = "Not enough senders."

            elif paid_task == 'ultimatum':
                my_role = p.participant.vars.get('ultimatum_role')
                if my_role == 'Proposer':
                    my_offer = target_round_player.ultimatum_offer
                    if my_offer is None: my_offer = 0
                    if pool_ultimatum_responder:
                        r_mao = random.choice(pool_ultimatum_responder)
                        if my_offer >= r_mao:
                            payoff = 100 - my_offer
                            explanation = f"You offered <b>{my_offer}</b>. Responder's MAO was {r_mao}. <b>Accepted</b>."
                        else:
                            payoff = 0
                            explanation = f"You offered <b>{my_offer}</b>. Responder's MAO was {r_mao}. <b>Rejected</b>."
                    else:
                        payoff = 0
                else:
                    my_mao = target_round_player.ultimatum_mao
                    if my_mao is None: my_mao = 0
                    if pool_ultimatum_proposer:
                        s_offer = random.choice(pool_ultimatum_proposer)
                        if s_offer >= my_mao:
                            payoff = s_offer
                            explanation = f"Proposer offered <b>{s_offer}</b>. Your MAO was {my_mao}. <b>Accepted</b>."
                        else:
                            payoff = 0
                            explanation = f"Proposer offered <b>{s_offer}</b>. Your MAO was {my_mao}. <b>Rejected</b>."
                    else:
                        payoff = 0

            elif paid_task == 'risk':
                scen_idx = random.randint(1, 4)
                field_name = f'risk_choice_{scen_idx}'
                choice = getattr(target_round_player, field_name)
                
                if choice == 'Option A':
                    payoff = Constants.risk_sure
                    explanation = f"Scenario {scen_idx} selected. You chose <b>Option A</b> (Safe)."
                else:
                    win_amount = Constants.risk_wins[scen_idx-1]
                    if random.random() < 0.5:
                        payoff = win_amount
                        explanation = f"Scenario {scen_idx} selected. You chose <b>Option B</b> and <b>WON</b>."
                    else:
                        payoff = 0
                        explanation = f"Scenario {scen_idx} selected. You chose <b>Option B</b> and <b>LOST</b>."

        except Exception as e:
            print(f"Error calculating payoff for player {p.id}: {e}")
            payoff = 0
            explanation = "Error in calculation."

        task_names = {
            'dictator': 'Allocation Task',
            'trust': 'Investment Task',
            'ultimatum': 'Proposal Task',
            'risk': 'Scenario Selection'
        }
        friendly_name = task_names.get(paid_task, paid_task.capitalize() + " Task")
        
        p.participant.vars['paid_task'] = friendly_name
        p.participant.vars['paid_tokens'] = int(payoff)
        p.participant.vars['payoff_explanation'] = explanation
        p.payoff = payoff

page_sequence = [
    IntroDecisionTasks,
    ShuffleWaitPage,
    Dictator,
    TrustSenderDecision, TrustSenderPrediction, TrustReceiverPlan,
    UltimatumProposer, UltimatumResponder,
    Risk,
    ComputePayoffsWaitPage
]