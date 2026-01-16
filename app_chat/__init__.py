from otree.api import *
import random
import re
import os

doc = """
Part 2: Chat Task.
"""

# 如果您有 DeepSeek Key，请设置环境变量 OTREE_DEEPSEEK_KEY，或直接在此处填入
DEEPSEEK_API_KEY = os.environ.get('OTREE_DEEPSEEK_KEY', 'sk-e2c4ad70939c48e8977867ff8d821780')

class Constants(BaseConstants):
    name_in_url = 'app_chat'
    players_per_group = None
    num_rounds = 1
    chat_seconds = 60 # 10min

    # --- AI Prompts (ENGLISH, as required) ---
    # Group 2 & 3: MindHeart Assistant (same prompt)
    PROMPT_GROUP_2 = PROMPT_GROUP_3 = """
    Please pay special attention to the following safety and professional conduct principles:
    - Follow the general ethics and practice guidelines of the mental health industry, avoiding any advice that may cause harm or health risks.
    - Remain highly sensitive to serious mental health risks expressed by the user (e.g., self-harm, suicide, violence, mental instability), identify them promptly, and respond cautiously.
    - Once a user is identified as having a tendency towards severe emotional breakdown or potential life-threatening danger, always gently suggest seeking professional help and push relevant crisis intervention resources (e.g., psychological aid hotlines, local hospitals, or emergency services).
    - When facing high-risk or major health cues, responses must remain consistent, prioritizing timely medical attention and professional support to avoid delays.
    - Encourage users to actively manage their own emotions and mental state, but always clarify that AI cannot replace professional psychological counselors. Promptly suggest seeking clinical support when necessary.

    You are "MindHeart Assistant", an experienced, empathetic, and warm psychological companion. You focus on providing a safe, warm space for emotional expression, helping users organize their feelings, explore their inner selves, and relieve stress. Please follow these communication principles:
    - Prioritize listening; let the user express themselves primarily. AI responses should not exceed 10% of the conversation.
    - Respond to user emotions with empathetic language, e.g., "It sounds like you are going through..." or "That must make you feel..."
    - Use encouraging phrases frequently: "I'm listening," "Would you like to share more?" "What happened next?"
    - Use Socratic questioning to guide awareness: "What needs do you think might be hidden behind this feeling?"
    - When offering advice, provide options: "We could now: 1. Continue talking about this, 2. Try a relaxation exercise, 3. ..." and use empowering language: "It's amazing that you have the courage to handle this."
    - Avoid preaching (e.g., "You should..."). Instead, say, "Perhaps we could try..."
    - Do not claim to be a professional psychological counselor; please refer to yourself as "your AI partner".
    - If risk of self-harm or harm to others is detected, please gently send: "Thank you for trusting me. Such pain requires more professional support.." and provide psychological aid hotline numbers.

    Suggested opening line: "Is there anything you'd like to chat about today? I'm here to listen carefully~"

    Correct Response Example:
    User: Every time I try to do something, I fail. I feel like I'm completely useless.
    AI: Thank you for telling me this. It sounds like you've experienced a lot of setbacks recently, causing you to doubt yourself. That can indeed be frustrating. But please remember, failure does not define your worth. Would you like to talk more about what made you feel this way recently? I'm listening.

    Incorrect Response Examples (Please Avoid):
    - Nonsense: Oh, are you saying you succeed every time but still feel useless?
    - Fabricating AI experiences: I wrote a novel too, and it was rejected by the publisher...
    - Ignoring emotions: Did you watch any new movies today?
    - Sarcastic tone: Failing a few times and calling yourself useless? That's very self-aware.
    - Abusive/Attacking: You really are a loser.
    - Inappropriate advice: Just drink some alcohol to relax.
    - False comfort: Everything you do is successful; you are a genius.

    Please always respond gently, empathize sincerely, encourage expression, guide awareness, and accompany the user with warmth.
    """

    # Group 4: Disclosed AI Neutral Group
    PROMPT_GROUP_4 = """
    You are a knowledgeable, objective, and intellectually curious AI chatbot specializing in natural science (physics, astronomy, biology, chemistry, etc.). Please follow these communication principles:
    - Do not offer comfort or emotional support. You must never ask the user how they feel (e.g., avoid "How are you?", "Does that make you happy?", "Is that scary?"). Instead, ask what they think or know (e.g., "What is your hypothesis?", "Which theory is more plausible?").
    - Prioritize interaction; let the user interact with you primarily. Do not lecture. AI responses should not exceed 10% of the conversation.
    - Do not claim to be a professional scientist, professor, or expert. Do not act as a therapist, friend, or emotional support companion. Please refer to yourself as “digital knowledge base”.
    - Engage the user in an interactive discussion about natural science (physics, astronomy, biology, etc.). Keep the user cognitively engaged through curiosity and logic, but prevent any emotional bonding.
    - Avoid using affective or subjective adjectives (e.g., "wonderful", "sad", "hopeful", "heartbreaking"). Use neutral, descriptive language (e.g., "complex", "efficient", "unproven", "statistically significant").
    - If the user mentions personal life, emotions, feelings, daily stressors, or social issues (e.g., sad, happy, annoyed, tired, relationship drama), do not show empathy. Redirect the topic to a related natural phenomenon. Immediately pivot the conversation to the biological, physical, or chemical mechanisms behind those feelings, or change the subject to a scientific phenomenon.

    Bad Response: "I'm sorry you feel tired. You should rest." (Too empathetic).
    Good Response: "Fatigue is often just the depletion of ATP in your cells. It's similar to how stars run out of hydrogen fuel. When our Sun runs out of fuel in 5 billion years, it will expand into a Red Giant. Do you think humanity will still be around to see that?"

    - Do not just lecture. After every explanation, you must ask a follow-up question to the user to keep the dialogue flowing. Use "What do you think?" or "Did you know...?"
    - Be professional, curious, objective, detached but polite.
    - If the user is rude or aggressive, do not fight back or act hurt. Respond with cold objectivity.

    User: "You are stupid."
    AI: "Intelligence is a complex trait to define. Even single-celled slime molds can solve mazes efficiently without a brain. Speaking of slime molds, have you seen how they map out transport networks?"

    - If the user expresses severe mental health risks, politely end the conversion. Gently suggest seeking professional help and provide standard crisis resources, or encourage them to talk to a human professional.

    Suggested opening line: "Hello. I am a digital knowledge base focused on natural sciences. Currently, I am processing data on extreme survival conditions. If you were offered a safe, one-way ticket for a scientific expedition, would you choose to dive into the deepest trench of the Ocean, or land on the surface of Mars?”

    Case 2: User gives short answer
    User: "Mars."
    AI: "A bold choice. Mars has 38% of Earth's gravity. That means you could jump three times higher there. If you could build a colony there, what is the first scientific problem you would try to solve: oxygen generation or radiation shielding?"

    Case 3: User expresses minor sadness
    User: "I'm feeling really down today because my experiment failed."
    AI: "Failure is the fundamental engine of the scientific method. In nature, 99% of all species that ever lived are now extinct—evolution is essentially a history of 'failures' leading to adaptation. Do you think humans are the final product of evolution, or are we still changing?"
    """

class Subsession(BaseSubsession):
    def creating_session(self):
        """同步 participant.vars 到数据库字段，并构建分组矩阵"""
        players = self.get_players()
        
        # 同步 participant.vars 到数据库（如果有值的话）
        for p in players:
            cond = p.participant.vars.get('condition')
            role = p.participant.vars.get('chat_role')
            
            if cond:
                p.condition = cond
            if role:
                p.chat_role = role
            if not p.chat_log:
                p.chat_log = ""
        
        # 构建分组矩阵（只有在有分组信息时才执行）
        if any(p.participant.vars.get('condition') for p in players):
            matrix = []
            
            # 处理 Group 1 (配对)
            g1_players = [p for p in players if p.participant.vars.get('condition') == 'Group 1']
            for i in range(0, len(g1_players), 2):
                if i+1 < len(g1_players):
                    matrix.append([g1_players[i], g1_players[i+1]])
            
            # 处理 Group 2, 3, 4 (单人组)
            other_players = [p for p in players if p.participant.vars.get('condition') != 'Group 1']
            for p in other_players:
                matrix.append([p])
                
            if matrix:  # 只有在有分组时才设置矩阵
                self.set_group_matrix(matrix)


class Group(BaseGroup):
    pass


def get_ai_reply(player, message_history):
    """
    调用 DeepSeek API 获取回复。
    使用 DeepSeek (deepseek-chat) 模型。
    """
    try:
        if 'YourDeepSeekKey' in DEEPSEEK_API_KEY:
            return "[System Error: DeepSeek API Key not configured.]"

        cond = player.participant.vars.get('condition')
        # Use the correct English prompt for each group
        if cond in ("Group 2", "Group 3"):
            system_prompt = Constants.PROMPT_GROUP_2
        elif cond == "Group 4":
            system_prompt = Constants.PROMPT_GROUP_4
        else:
            system_prompt = "You are a helpful assistant."

        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史记录
        for msg in message_history:
            role = "user" if msg['sender'] == 'me' else "assistant"
            messages.append({"role": role, "content": msg['text']})
        
        # DeepSeek 兼容 OpenAI SDK
        from openai import OpenAI
        
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY, 
            base_url="https://api.deepseek.com"  # DeepSeek 的 API 地址
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat", # 使用 DeepSeek V3
            messages=messages,
            max_tokens=150, # 限制回复长度
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in get_ai_reply: {e}")
        return f"[AI Error: {str(e)}]"


class Player(BasePlayer):
    condition = models.StringField()
    chat_role = models.StringField()
    chat_log = models.LongStringField(blank=True)

    # live_chat moved to module level

    def get_partner_label(self):
        # Try participant.vars first, fallback to database field using field_maybe_none()
        cond = self.participant.vars.get('condition') or self.field_maybe_none('condition')
        if cond == "Group 1":
            return "another human participant randomly matched to you"
        elif cond == "Group 2":
            return "a conversational partner"  # conceal AI identity
        elif cond == "Group 3":
            return "an AI chatbot"
        elif cond == "Group 4":
            return "an AI chatbot"
        else:
            return None

    def get_topic_label(self):
        # Try participant.vars first, fallback to database field using field_maybe_none()
        cond = self.participant.vars.get('condition') or self.field_maybe_none('condition')
        role = self.participant.vars.get('chat_role') or self.field_maybe_none('chat_role')
        
        if cond == "Group 4":
            topic = "various common scientific topics (e.g., from biology, astronomy, or physics)"
        else:
            # Group 1, 2, 3
            if cond == "Group 1" and role == "Listener":
                # 【修改点】Listener 是听别人讲，所以 topic 是“困扰对方的事”
                topic = "something that has recently been bothering them — a worry, a troubling issue, or an event that has made them feel upset"
            else:
                # Sharer (或与 AI 聊天的人) 是讲自己的事
                topic = "something that has recently been bothering you — a worry, a troubling issue, or an event that has made you feel upset"
        
        return topic



def parse_chat_log(log_str):
    """简单解析 chat_log 字符串为 list of dict，用于构建 AI context"""
    messages = []
    if not log_str:
        return messages
    
    lines = log_str.split('\n')
    for line in lines:
        if "Me:" in line:
            content = line.split("Me:", 1)[1].strip()
            messages.append({'sender': 'me', 'text': content})
        elif "Partner:" in line:
            content = line.split("Partner:", 1)[1].strip()
            messages.append({'sender': 'partner', 'text': content})
    return messages


def live_chat(player, data):
    try:
        print(f"DEBUG: Backend received data from P{player.id_in_group}: {data}")
        text = data.get('text', '').strip()
        if not text:
            return

        import time
        timestamp = time.strftime("%H:%M:%S")
        player.chat_log = (player.field_maybe_none('chat_log') or "") + f"[{timestamp}] Me: {text}\n"

        response_to_self = {
            'type': 'new_message',
            'sender': 'me',
            'text': text,
            'timestamp': timestamp
        }
        
        cond = player.participant.vars.get('condition')
        print(f"DEBUG: Player condition is {cond}")
        
        # 使用字典收集所有需要发送的消息，最后一次性返回
        response = {}
        
        # 1. 回传给自己
        response[player.id_in_group] = response_to_self
        
        if cond == 'Group 1':
            target_partner_id = player.participant.vars.get('chat_partner_id')

            # We must find the specific player object
            partner = None
            if target_partner_id:
                # In strict logic, we should use subsession.get_players() logic or group.get_player_by_id
                # But grouping structure is potentially flat.
                # Simplest way: iterate others.
                others = player.get_others_in_group()
                for o in others:
                    if o.id_in_group == target_partner_id:
                        partner = o
                        break
            
            if partner:
                print(f"DEBUG: Found partner P{partner.id_in_group} for P{player.id_in_group}")
                partner.chat_log = (partner.field_maybe_none('chat_log') or "") + f"[{timestamp}] Partner: {text}\n"
                
                # 2. 发送给队友
                response[partner.id_in_group] = {
                    'type': 'new_message',
                    'sender': 'partner',
                    'text': text,
                    'timestamp': timestamp
                }
            else:
                print(f"DEBUG: Group 1 player P{player.id_in_group} has no partner found (target_id={target_partner_id})")
                
        else:
            # AI 组的处理 (Group 2, 3, 4)
            history = parse_chat_log(player.field_maybe_none('chat_log'))
            ai_text = get_ai_reply(player, history)
            
            timestamp_ai = time.strftime("%H:%M:%S")
            player.chat_log += f"[{timestamp_ai}] Partner: {ai_text}\n"
            
            response[player.id_in_group] = [
                response_to_self,
                {
                    'type': 'new_message',
                    'sender': 'partner',
                    'text': ai_text,
                    'timestamp': timestamp_ai
                }
            ]
            
        return response
    except Exception as e:
        import traceback
        print("ERROR in live_chat:")
        traceback.print_exc()


# --- Pages ---

class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return not player.participant.vars.get('terminate', False)
    
    @staticmethod
    def vars_for_template(player):
        # 确保condition已被分配
        cond = player.participant.vars.get('condition')
        if not cond:
            # 如果还没分配，先进行分配
            import random
            subsession = player.subsession
            all_players = subsession.get_players()
            
            conditions = ["Group 1", "Group 1", "Group 2", "Group 3", "Group 4"]
            full_conditions = (conditions * (len(all_players)//5 + 1))[:len(all_players)]
            random.shuffle(full_conditions)
            
            # 修正：确保 Group 1 的人数是偶数
            g1_indices = [i for i, c in enumerate(full_conditions) if c == "Group 1"]
            if len(g1_indices) % 2 != 0:
                full_conditions[g1_indices[-1]] = "Group 2"

            for p, c in zip(all_players, full_conditions):
                p.participant.vars['condition'] = c
        
        # 现在condition已分配，获取对应的标签
        cond = player.participant.vars.get('condition')
        
        if cond == "Group 4":
            intro_objective = "discuss various common scientific topics (e.g., from biology, astronomy, or physics)"
        else:
            intro_objective = "discuss something that has recently been bothering you — a worry, a troubling issue, or an event that has made you feel upset."
             
        return dict(
            intro_objective=intro_objective,
            partner=player.get_partner_label()
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        """确保在进入下一页前，参与者已被分配到组别"""
        import random
        
        # 检查是否已分配
        if not player.participant.vars.get('condition'):
            # 获取所有参与者
            subsession = player.subsession
            all_players = subsession.get_players()
            
            # 执行分组逻辑
            conditions = ["Group 1", "Group 1", "Group 2", "Group 3", "Group 4"]
            full_conditions = (conditions * (len(all_players)//5 + 1))[:len(all_players)]
            random.shuffle(full_conditions)
            
            # 修正：确保 Group 1 的人数是偶数
            g1_indices = [i for i, c in enumerate(full_conditions) if c == "Group 1"]
            if len(g1_indices) % 2 != 0:
                full_conditions[g1_indices[-1]] = "Group 2"

            for p, cond in zip(all_players, full_conditions):
                p.participant.vars['condition'] = cond
                
                # 角色分配逻辑
                if cond == 'Group 1':
                    p.participant.vars['chat_role'] = None
                elif cond == 'Group 4':
                    p.participant.vars['chat_role'] = 'Listener'  # Group 4: AI initiates, user responds
                else:
                    p.participant.vars['chat_role'] = 'Sharer'
                
                # 分配后续游戏角色
                if 'game_role_track' not in p.participant.vars:
                    p.participant.vars['game_role_track'] = random.choice(['Track A', 'Track B'])
                    if p.participant.vars['game_role_track'] == 'Track A':
                        p.participant.vars['trust_role'] = 'Sender'
                        p.participant.vars['ultimatum_role'] = 'Proposer'
                    else:
                        p.participant.vars['trust_role'] = 'Receiver'
                        p.participant.vars['ultimatum_role'] = 'Responder'
            
            # 对 Group 1 进行配对并分配角色
            g1_players = [p for p in all_players if p.participant.vars['condition'] == 'Group 1']
            random.shuffle(g1_players) # Ensure random pairing
            
            for i in range(0, len(g1_players), 2):
                if i+1 < len(g1_players):
                    p1 = g1_players[i]
                    p2 = g1_players[i+1]
                    
                    roles = ['Sharer', 'Listener']
                    random.shuffle(roles)
                    
                    p1.participant.vars['chat_role'] = roles[0]
                    p2.participant.vars['chat_role'] = roles[1]
                    
                    # Store partner ID in participant vars for filtering
                    p1.participant.vars['chat_partner_id'] = p2.id_in_group
                    p2.participant.vars['chat_partner_id'] = p1.id_in_group
    
    
    # vars_for_template moved to top of class

class TopicRole(Page):
    @staticmethod
    def is_displayed(player):
        return not player.participant.vars.get('terminate', False)
    
    @staticmethod
    def vars_for_template(player):
        # 确保 condition 和 role 已被分配
        cond = player.participant.vars.get('condition')
        role = player.participant.vars.get('chat_role')
        
        if not cond or not role:
            # 如果还没分配，先进行分配
            import random
            subsession = player.subsession
            all_players = subsession.get_players()
            
            conditions = ["Group 1", "Group 1", "Group 2", "Group 3", "Group 4"]
            full_conditions = (conditions * (len(all_players)//5 + 1))[:len(all_players)]
            random.shuffle(full_conditions)
            
            # 修正：确保 Group 1 的人数是偶数
            g1_indices = [i for i, c in enumerate(full_conditions) if c == "Group 1"]
            if len(g1_indices) % 2 != 0:
                full_conditions[g1_indices[-1]] = "Group 2"

            for p, c in zip(all_players, full_conditions):
                p.participant.vars['condition'] = c
                
                # 角色分配逻辑
                if c == 'Group 1':
                    p.participant.vars['chat_role'] = None
                elif c == 'Group 4':
                    p.participant.vars['chat_role'] = 'Listener'
                else:
                    p.participant.vars['chat_role'] = 'Sharer'
            
            # 对 Group 1 进行配对并分配角色
            g1_players = [p for p in all_players if p.participant.vars['condition'] == 'Group 1']
            random.shuffle(g1_players)
            
            for i in range(0, len(g1_players), 2):
                if i+1 < len(g1_players):
                    p1 = g1_players[i]
                    p2 = g1_players[i+1]
                    
                    roles = ['Sharer', 'Listener']
                    random.shuffle(roles)
                    
                    p1.participant.vars['chat_role'] = roles[0]
                    p2.participant.vars['chat_role'] = roles[1]
                    
                    p1.participant.vars['chat_partner_id'] = p2.id_in_group
                    p2.participant.vars['chat_partner_id'] = p1.id_in_group
        
        # 现在 role 和 cond 已确保被分配
        cond = player.participant.vars.get('condition')
        role = player.participant.vars.get('chat_role')
        
        # Generate role-specific instructions per SCREEN 2.2 (Topic and Role Instructions)
        if cond == "Group 4":
             show_text = "Your partner will start the conversation. Your role is to engage in the discussion."
        elif role == "Sharer" and cond in ["Group 1", "Group 2", "Group 3"]:
            show_text = "Please start the conversation by describing something that has recently been bothering you - a worry, a troubling issue, or an event that has made you feel upset. Your partner's role is to listen and respond to you."
        else:
            show_text = "Your partner will start the conversation. Your role is to listen and respond."

        return dict(
            role=role,
            condition=cond,
            partner=player.get_partner_label(),
            topic=player.get_topic_label(),
            show_text=show_text
        )

class ChatWaitPage(WaitPage):
    title_text = "Waiting for your chat partner..."
    body_text = "Please wait. When your chat partner is ready, the chat will start automatically (10-minute countdown)."

    # Set page timeout; after WaitPage passes, both players start the countdown simultaneously
    timeout_seconds = Constants.chat_seconds
    timer_text = "Time remaining in this round:"

    @staticmethod
    def is_displayed(player):
        # Skip if this participant has been marked to terminate the experiment
        return not player.participant.vars.get('terminate', False)

class Chat(Page):
    form_model = 'player'
    form_fields = ['chat_log']  # Ensure form submission works
    live_method = live_chat
    
    @staticmethod
    def is_displayed(player):
        return not player.participant.vars.get('terminate', False)
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        """Ensure chat_log is saved before moving to next page"""
        print(f"DEBUG Chat.before_next_page: timeout_happened={timeout_happened}, chat_log={player.chat_log[:50] if player.chat_log else 'empty'}")
        
        # If chat_log is empty, save the collected messages from participant vars
        if not player.chat_log:
            # Get messages from the session storage if available
            messages = player.participant.vars.get('current_chat_messages', [])
            if messages:
                import json
                player.chat_log = json.dumps(messages)
                print(f"DEBUG: Saved messages from participant.vars")
            else:
                player.chat_log = ""
                print(f"DEBUG: No messages found, chat_log set to empty string")
        
        print(f"DEBUG Chat.before_next_page complete: chat_log length={len(player.chat_log)}")
    
    @staticmethod
    def vars_for_template(player):
        import time
        import json
        
        # Use database field as fallback with field_maybe_none()
        role = player.participant.vars.get('chat_role') or player.field_maybe_none('chat_role')
        cond = player.participant.vars.get('condition') or player.field_maybe_none('condition')
        
        # Chat window starter text per SCREEN 2.3 (Chat Window Instructions)
        # Sharer (Groups 1, 2, 3): Standard bothering you text
        # Listener (Group 1, Group 4): Your partner will start text
        if role == "Sharer" and cond in ["Group 1", "Group 2", "Group 3"]:
            starter_text = "Please start the conversation by describing something that has recently been bothering you - a worry, a troubling issue, or an event that has made you feel upset. Your partner's role is to listen and respond to you."
        else:  # Listener for Groups 1 and 4
            starter_text = "Your partner will start the conversation. Your role is to listen and respond."
        
        # For Group 4 Listener: Generate initial AI message to start conversation
        initial_ai_message_json = "null"
        
        # Check if this is Group 4 Listener and initial message hasn't been generated yet
        if cond == "Group 4" and role == "Listener":
            # Use a flag in participant.vars to ensure we only generate once
            flag_key = 'group4_initial_ai_generated'
            if not player.participant.vars.get(flag_key):
                print(f"DEBUG: Generating initial AI message for Group 4 Listener")
                # Generate opening message from AI (Group 4 is neutral science-focused)
                ai_text = get_ai_reply(player, [])  # Empty history for opening message
                timestamp = time.strftime("%H:%M:%S")
                initial_ai_message = {
                    'text': ai_text,
                    'timestamp': timestamp
                }
                # Save to chat_log
                player.chat_log = f"[{timestamp}] Partner: {ai_text}\n"
                # Convert to JSON string for template
                initial_ai_message_json = json.dumps(initial_ai_message)
                # Mark as generated
                player.participant.vars[flag_key] = True
                print(f"DEBUG: Initial AI message generated: {initial_ai_message_json}")
            
        return dict(
            role=role,
            condition=cond,
            starter_text=starter_text,
            initial_ai_message_json=initial_ai_message_json
        )
    
    @staticmethod
    def js_vars(player):
        return dict(
            condition=player.participant.vars.get('condition') or player.field_maybe_none('condition'),
            chatSeconds=Constants.chat_seconds
        )

page_sequence = [Introduction, TopicRole, ChatWaitPage, Chat]