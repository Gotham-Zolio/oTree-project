from otree.api import *
import random

doc = """
Part 3: Decision Tasks.
"""

class Constants(BaseConstants):
    name_in_url = 'app_games'
    players_per_group = None
    num_rounds = 4
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
        """初始化游戏变量，确保app_chat的数据被正确传递"""
        for player in self.get_players():
            # 确保参与者变量已初始化
            ensure_participant_vars(player.participant)

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # --- 1. Dictator Game (Allocation Task) ---
    dictator_sent = models.IntegerField(min=0, max=Constants.endowment)
    
    # --- 2. Trust Game (Investment Task) ---
    trust_sent = models.IntegerField(choices=Constants.trust_send_options)
    trust_prediction = models.IntegerField(min=0, max=Constants.trust_multiplier * Constants.endowment)
    
    # Trust Receiver 策略法
    trust_return_25 = models.IntegerField(min=0, max=Constants.trust_multiplier * 25)
    trust_return_50 = models.IntegerField(min=0, max=Constants.trust_multiplier * 50)
    trust_return_75 = models.IntegerField(min=0, max=Constants.trust_multiplier * 75)
    trust_return_100 = models.IntegerField(min=0, max=Constants.trust_multiplier * 100)
    
    # --- 3. Ultimatum Game (Proposal/Response Task) ---
    ultimatum_offer = models.IntegerField(min=0, max=Constants.endowment)
    ultimatum_mao = models.IntegerField(min=0, max=Constants.endowment)
    
    # --- 4. Risk Game (Scenario Selection) ---
    risk_choice_1 = models.StringField(choices=[["A", "Option A"], ["B", "Option B"]])
    risk_choice_2 = models.StringField(choices=[["A", "Option A"], ["B", "Option B"]])
    risk_choice_3 = models.StringField(choices=[["A", "Option A"], ["B", "Option B"]])
    risk_choice_4 = models.StringField(choices=[["A", "Option A"], ["B", "Option B"]])
    
    # --- 支付字段 ---
    paid_task = models.StringField(blank=True)
    paid_tokens = models.IntegerField(blank=True)

# --- 辅助函数 ---

def ensure_participant_vars(participant):
    if participant.vars.get('terminate', False): return
    if 'condition' not in participant.vars: participant.vars['condition'] = random.choice(["Group 1", "Group 2"])
    if 'chat_role' not in participant.vars: participant.vars['chat_role'] = "Sharer"
    if 'game_role_track' not in participant.vars: participant.vars['game_role_track'] = random.choice(["Track A", "Track B"])
    
    if 'trust_role' not in participant.vars:
        track = participant.vars['game_role_track']
        participant.vars['trust_role'] = "Sender" if track == "Track A" else "Receiver"
        participant.vars['ultimatum_role'] = "Proposer" if track == "Track A" else "Responder"
        
    if 'task_sequence' not in participant.vars:
        seq = TASKS.copy()
        random.shuffle(seq)
        participant.vars['task_sequence'] = seq
        
    # 初始化 decisions 字典，确保所有字段都存在
    if 'decisions' not in participant.vars: 
        participant.vars['decisions'] = {
            'dictator_sent': 0,
            'trust_sent': 0,
            'trust_prediction': 0,
            'trust_return_plan': {},
            'ultimatum_offer': 0,
            'ultimatum_mao': 0,
            'risk_choices': ['A', 'A', 'A', 'A']
        }

def get_current_task(player):
    seq = player.participant.vars.get('task_sequence', TASKS)
    idx = player.round_number - 1
    if idx < 0 or idx >= len(seq): return seq[-1]
    return seq[idx]

def compute_final_payoffs(subsession):
    try:
        print(f"DEBUG: compute_final_payoffs called for subsession {subsession.id}")
        session = subsession.session
        if session.vars.get('payoffs_calculated', False): 
            print("DEBUG: Payoffs already calculated, skipping")
            return
        
        players = subsession.get_players()
        print(f"DEBUG: Total players: {len(players)}")
        active_players = [p for p in players if not p.participant.vars.get('terminate', False)]
        active_parts = [p.participant for p in active_players]
        print(f"DEBUG: Active players: {len(active_players)}")
        
        # 1. 建立数据池
        pool_dictator_sent = [int(p.vars.get('decisions', {}).get('dictator_sent', 0)) for p in active_parts]
        
        pool_trust_senders = []
        pool_trust_receivers = []
        for p in active_parts:
            if p.vars.get('trust_role') == 'Sender':
                pool_trust_senders.append(int(p.vars.get('decisions', {}).get('trust_sent', 0)))
            else:
                pool_trust_receivers.append(p.vars.get('decisions', {}).get('trust_return_plan', {}))
                
        pool_ult_proposers = []
        pool_ult_responders = []
        for p in active_parts:
            if p.vars.get('ultimatum_role') == 'Proposer':
                pool_ult_proposers.append(int(p.vars.get('decisions', {}).get('ultimatum_offer', 0)))
            else:
                pool_ult_responders.append(int(p.vars.get('decisions', {}).get('ultimatum_mao', 0)))

        def safe_choice(pool, default):
            return random.choice(pool) if pool else default

        # 2. 计算收益 (Shadow Matching)
        for pt in active_parts:
            pt.vars['potential_payoffs'] = {}
            pt.vars['task_roles'] = {} 
            pt.vars['task_details'] = {}
            
            # --- Dictator ---
            if random.random() < 0.5:
                sent = int(pt.vars.get('decisions', {}).get('dictator_sent', 0))
                pt.vars['potential_payoffs']['dictator'] = (Constants.endowment - sent)
                pt.vars['task_roles']['dictator'] = "Sender"
                pt.vars['task_details']['dictator'] = {'sent': sent}
            else:
                received = safe_choice(pool_dictator_sent, 0)
                pt.vars['potential_payoffs']['dictator'] = received
                pt.vars['task_roles']['dictator'] = "Recipient"
                pt.vars['task_details']['dictator'] = {'received': received}

            # --- Trust ---
            role = pt.vars.get('trust_role')
            pt.vars['task_roles']['trust'] = role
            
            if role == 'Sender':
                my_sent = int(pt.vars.get('decisions', {}).get('trust_sent', 0))
                fallback_plan = {0:0, 25:12, 50:25, 75:37, 100:50} 
                partner_plan = safe_choice(pool_trust_receivers, fallback_plan)
                actual_returned = int(partner_plan.get(my_sent, 0))
                
                # Bonus logic
                prediction = int(pt.vars.get('decisions', {}).get('trust_prediction', -999))
                bonus = 0
                if abs(prediction - actual_returned) <= Constants.trust_prediction_error:
                    bonus = Constants.trust_prediction_bonus
                
                pt.vars['potential_payoffs']['trust'] = (Constants.endowment - my_sent) + actual_returned + bonus
                pt.vars['task_details']['trust'] = {
                    'my_sent': my_sent, 'actual_returned': actual_returned, 'bonus': bonus
                }
            else:
                partner_sent = safe_choice(pool_trust_senders, 50)
                my_plan = pt.vars.get('decisions', {}).get('trust_return_plan', {})
                my_return = int(my_plan.get(partner_sent, 0))
                pt.vars['potential_payoffs']['trust'] = (partner_sent * Constants.trust_multiplier) - my_return
                pt.vars['task_details']['trust'] = {
                    'partner_sent': partner_sent, 'my_return': my_return
                }

            # --- Ultimatum ---
            role = pt.vars.get('ultimatum_role')
            pt.vars['task_roles']['ultimatum'] = role
            if role == 'Proposer':
                my_offer = int(pt.vars.get('decisions', {}).get('ultimatum_offer', 0))
                partner_mao = safe_choice(pool_ult_responders, 40)
                success = my_offer >= partner_mao
                pt.vars['potential_payoffs']['ultimatum'] = (Constants.endowment - my_offer) if success else 0
                pt.vars['task_details']['ultimatum'] = {
                    'my_offer': my_offer, 'partner_mao': partner_mao, 'success': success
                }
            else:
                my_mao = int(pt.vars.get('decisions', {}).get('ultimatum_mao', 0))
                partner_offer = safe_choice(pool_ult_proposers, 50)
                success = partner_offer >= my_mao
                pt.vars['potential_payoffs']['ultimatum'] = partner_offer if success else 0
                pt.vars['task_details']['ultimatum'] = {
                    'partner_offer': partner_offer, 'my_mao': my_mao, 'success': success
                }

            # --- Risk ---
            pt.vars['risk_choices_list'] = pt.vars.get('decisions', {}).get('risk_choices', ["A"]*4)

        # 3. 最终抽取与生成解释文案
        for p in players:
            pt = p.participant
            if pt.vars.get('terminate', False): continue
            
            selected = random.choice(TASKS)
            tokens = 0
            explanation = ""
            final_task_display_name = ""
            
            # === Risk (Scenario Selection) ===
            if selected == 'risk':
                sc_idx = random.randint(0, 3)
                choice = pt.vars['risk_choices_list'][sc_idx]
                
                is_win = False
                if choice == "A":
                    tokens = Constants.risk_sure
                    outcome_text = f"Since you chose Option A (Safe), you received the guaranteed {tokens} tokens."
                else:
                    is_win = random.random() < 0.5
                    win_amt = Constants.risk_wins[sc_idx]
                    tokens = win_amt if is_win else 0
                    outcome_text = f"You chose Option B (Risky). The random coin flip resulted in a {'WIN' if is_win else 'LOSS'}."
                
                explanation = (
                    f"The system randomly selected <b>Scenario {sc_idx + 1}</b> for payment.<br>"
                    f"{outcome_text}<br>"
                    f"<b>Total Earnings: {tokens} tokens.</b>"
                )
                final_task_display_name = f"Scenario Selection (Scenario {sc_idx + 1})"
                
            # === Dictator (Allocation Task) ===
            elif selected == 'dictator':
                role = pt.vars['task_roles']['dictator']
                details = pt.vars['task_details']['dictator']
                tokens = pt.vars['potential_payoffs']['dictator']
                
                if role == "Sender":
                    sent = details['sent']
                    explanation = (
                        f"You were randomly assigned the role of <b>Sender</b>.<br>"
                        f"You chose to give <b>{sent} tokens</b> to the Receiver.<br>"
                        f"Therefore, you kept the rest: 100 - {sent} = <b>{tokens} tokens</b>."
                    )
                else:
                    received = details['received']
                    explanation = (
                        f"You were randomly assigned the role of <b>Receiver</b>.<br>"
                        f"The Sender matched with you chose to give you <b>{received} tokens</b>.<br>"
                        f"Therefore, your earnings are <b>{tokens} tokens</b>."
                    )
                final_task_display_name = f"Allocation Task ({role})"
                
            # === Trust (Investment Task) ===
            elif selected == 'trust':
                role = pt.vars['task_roles']['trust']
                details = pt.vars['task_details']['trust']
                tokens = pt.vars['potential_payoffs']['trust']
                
                if role == "Sender":
                    my_sent = details['my_sent']
                    actual_returned = details['actual_returned']
                    bonus = details['bonus']
                    explanation = (
                        f"You were the <b>Sender</b>.<br>"
                        f"You sent <b>{my_sent} tokens</b>. The Receiver decided to return <b>{actual_returned} tokens</b> to you.<br>"
                        f"Game Earnings: (100 - {my_sent}) + {actual_returned} = {tokens - bonus}.<br>"
                    )
                    if bonus > 0:
                        explanation += f"<span class='text-success'><b>Bonus:</b> Your prediction was correct! (+{bonus} tokens).</span><br>"
                    explanation += f"<b>Total Earnings: {tokens} tokens.</b>"
                else:
                    partner_sent = details['partner_sent']
                    my_return = details['my_return']
                    explanation = (
                        f"You were the <b>Receiver</b>.<br>"
                        f"The Sender matched with you sent <b>{partner_sent} tokens</b> (which tripled to {partner_sent * 3}).<br>"
                        f"Based on your strategy plan for this amount, you decided to return <b>{my_return} tokens</b>.<br>"
                        f"You kept the rest: {partner_sent * 3} - {my_return} = <b>{tokens} tokens</b>."
                    )
                final_task_display_name = f"Investment Task ({role})"
                
            # === Ultimatum (Proposal / Response Task) ===
            elif selected == 'ultimatum':
                role = pt.vars['task_roles']['ultimatum']
                details = pt.vars['task_details']['ultimatum']
                tokens = pt.vars['potential_payoffs']['ultimatum']
                
                if role == "Proposer":
                    my_offer = details['my_offer']
                    partner_mao = details['partner_mao']
                    success = details['success']
                    result_str = "ACCEPTED" if success else "REJECTED"
                    color = "text-success" if success else "text-danger"
                    explanation = (
                        f"You were the <b>Proposer</b>.<br>"
                        f"You offered <b>{my_offer} tokens</b>. The Responder's Minimum Acceptable Offer (MAO) was <b>{partner_mao}</b>.<br>"
                        f"Result: Your offer was <b class='{color}'>{result_str}</b>.<br>"
                    )
                    if success:
                        explanation += f"You kept: 100 - {my_offer} = <b>{tokens} tokens</b>."
                    else:
                        explanation += "Both of you received <b>0 tokens</b>."
                    final_task_display_name = f"Proposal Task ({role})"
                    
                else:
                    partner_offer = details['partner_offer']
                    my_mao = details['my_mao']
                    success = details['success']
                    result_str = "ACCEPTED" if success else "REJECTED"
                    color = "text-success" if success else "text-danger"
                    explanation = (
                        f"You were the <b>Responder</b>.<br>"
                        f"The Proposer offered <b>{partner_offer} tokens</b>. Your Minimum Acceptable Offer (MAO) was <b>{my_mao}</b>.<br>"
                        f"Result: The offer was <b class='{color}'>{result_str}</b>.<br>"
                    )
                    if success:
                        explanation += f"You received the offer of <b>{tokens} tokens</b>."
                    else:
                        explanation += "Both of you received <b>0 tokens</b>."
                    final_task_display_name = f"Response Task ({role})"

            # 4. 存入 participant.vars
            p.paid_task = final_task_display_name
            p.paid_tokens = int(tokens)
            p.payoff = tokens
            
            pt.vars['paid_task'] = final_task_display_name
            pt.vars['paid_tokens'] = int(tokens)
            pt.vars['payoff_explanation'] = explanation
        
        session.vars['payoffs_calculated'] = True
        print("DEBUG: Payoffs calculation completed successfully")
        
    except Exception as e:
        import traceback
        print(f"ERROR in compute_final_payoffs: {e}")
        traceback.print_exc()
        session = subsession.session
        session.vars['payoffs_calculated'] = True  # Mark as done even on error to prevent infinite loop

# --- Pages ---

class ShuffleWaitPage(Page):
    @staticmethod
    def is_displayed(player): 
        return player.round_number == 1 and not player.participant.vars.get('terminate', False)
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        ensure_participant_vars(player.participant)

class Dictator(Page):
    form_model = 'player'
    form_fields = ['dictator_sent']
    @staticmethod
    def is_displayed(player): return (not player.participant.vars.get('terminate', False)) and (get_current_task(player) == 'dictator')
    @staticmethod
    def before_next_page(player, timeout_happened):
        ensure_participant_vars(player.participant)
        player.participant.vars['decisions']['dictator_sent'] = player.dictator_sent

class TrustSenderDecision(Page):
    form_model = 'player'
    form_fields = ['trust_sent']
    @staticmethod
    def is_displayed(player):
        ensure_participant_vars(player.participant)
        return (not player.participant.vars.get('terminate', False)) and (get_current_task(player) == 'trust') and (player.participant.vars.get('trust_role') == 'Sender')
    @staticmethod
    def before_next_page(player, timeout_happened):
        ensure_participant_vars(player.participant)
        player.participant.vars['decisions']['trust_sent'] = player.trust_sent

class TrustSenderPrediction(Page):
    form_model = 'player'
    form_fields = ['trust_prediction']
    
    @staticmethod
    def is_displayed(player): 
        return (not player.participant.vars.get('terminate', False)) and \
               (get_current_task(player) == 'trust') and \
               (player.participant.vars.get('trust_role') == 'Sender')
    
    @staticmethod
    def vars_for_template(player):
        return dict(
            sent=player.trust_sent,
            tripled=(player.trust_sent or 0) * 3
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        ensure_participant_vars(player.participant)
        player.participant.vars['decisions']['trust_prediction'] = player.trust_prediction

class TrustReceiverPlan(Page):
    form_model = 'player'
    form_fields = ['trust_return_25', 'trust_return_50', 'trust_return_75', 'trust_return_100']
    @staticmethod
    def is_displayed(player):
        ensure_participant_vars(player.participant)
        return (not player.participant.vars.get('terminate', False)) and (get_current_task(player) == 'trust') and (player.participant.vars.get('trust_role') == 'Receiver')
    @staticmethod
    def before_next_page(player, timeout_happened):
        ensure_participant_vars(player.participant)
        plan = {0:0, 25:player.trust_return_25, 50:player.trust_return_50, 75:player.trust_return_75, 100:player.trust_return_100}
        player.participant.vars['decisions']['trust_return_plan'] = plan

class UltimatumProposer(Page):
    form_model = 'player'
    form_fields = ['ultimatum_offer']
    @staticmethod
    def is_displayed(player):
        ensure_participant_vars(player.participant)
        return (not player.participant.vars.get('terminate', False)) and (get_current_task(player) == 'ultimatum') and (player.participant.vars.get('ultimatum_role') == 'Proposer')
    @staticmethod
    def before_next_page(player, timeout_happened):
        ensure_participant_vars(player.participant)
        player.participant.vars['decisions']['ultimatum_offer'] = player.ultimatum_offer

class UltimatumResponder(Page):
    form_model = 'player'
    form_fields = ['ultimatum_mao']
    @staticmethod
    def is_displayed(player):
        ensure_participant_vars(player.participant)
        return (not player.participant.vars.get('terminate', False)) and (get_current_task(player) == 'ultimatum') and (player.participant.vars.get('ultimatum_role') == 'Responder')
    @staticmethod
    def before_next_page(player, timeout_happened):
        ensure_participant_vars(player.participant)
        player.participant.vars['decisions']['ultimatum_mao'] = player.ultimatum_mao

class Risk(Page):
    form_model = 'player'
    form_fields = ['risk_choice_1', 'risk_choice_2', 'risk_choice_3', 'risk_choice_4']
    @staticmethod
    def is_displayed(player): return (not player.participant.vars.get('terminate', False)) and (get_current_task(player) == 'risk')
    @staticmethod
    def before_next_page(player, timeout_happened):
        ensure_participant_vars(player.participant)
        player.participant.vars['decisions']['risk_choices'] = [player.risk_choice_1, player.risk_choice_2, player.risk_choice_3, player.risk_choice_4]

class ComputePayoffsWaitPage(WaitPage):
    title_text = "Calculating Payoffs"
    body_text = "Please wait while the system calculates the payoffs and performs the random matching."
    
    @staticmethod
    def is_displayed(player): 
        return player.round_number == Constants.num_rounds and not player.participant.vars.get('terminate', False)
    
    @staticmethod
    def after_all_players_arrive(group):
        """所有players都到达时，统一计算payoffs"""
        subsession = group.subsession
        print(f"DEBUG: ComputePayoffsWaitPage.after_all_players_arrive called for subsession {subsession.id}")
        compute_final_payoffs(subsession)
        print(f"DEBUG: compute_final_payoffs completed for subsession {subsession.id}")

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds and not player.participant.vars.get('terminate', False)
    
    @staticmethod
    def vars_for_template(player):
        pt = player.participant
        paid_task = pt.vars.get('paid_task', 'Unknown')
        paid_tokens = pt.vars.get('paid_tokens', 0)
        
        return dict(
            paid_task=paid_task,
            paid_tokens=paid_tokens
        )

page_sequence = [
    ShuffleWaitPage,
    Dictator,
    TrustSenderDecision, TrustSenderPrediction, TrustReceiverPlan,
    UltimatumProposer, UltimatumResponder,
    Risk,
    ComputePayoffsWaitPage,
    Results
]