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
    ses1 = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="1.")
    ses2 = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="2.")
    ses3 = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="3.")
    ses4 = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="4.")
    ses5 = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="5.")
    ses6 = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="6.")
    
    # --- 3. Decision Factors (Review of Tasks) ---
    f1 = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="1.")
    f2 = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="2.")
    f3 = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="3.")
    f4 = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="4.")
    
    # --- 4. Other (Final Question) ---
    human_likeness = models.IntegerField(
        choices=LIKERT_7, 
        label="To what extent did you feel you were talking to a real human?", 
        widget=widgets.RadioSelectHorizontal
    )
    
    # --- 5. Demographics (Complete Version) ---
    
    # Q1. Age
    age = models.IntegerField(min=18, max=100, label="What is your age?")
    
    # Q2. Gender
    gender = models.StringField(
        choices=["Male", "Female", "Non-binary", "Prefer not to say"], 
        label="What is your gender?",
        widget=widgets.RadioSelect
    )
    
    # Q3. Nationality
    nationality = models.StringField(label="What is your nationality?")
    
    # Q4. Race (Select all that apply)
    # 注意：多选框在 oTree 中通常存储为字符串。
    race = models.StringField(
        label="What is your race? (Please select all that apply)",
        widget=widgets.CheckboxSelectMultiple,
        choices=[
            "American Indian or Alaska Native",
            "Asian",
            "Black or African American",
            "Native Hawaiian or Other Pacific Islander",
            "White",
            "Other",
            "Prefer not to say"
        ]
    )
    
    # Q5. Education
    education = models.StringField(
        label="What is your highest level of education completed?",
        choices=[
            "High school or less",
            "Some college, no degree",
            "Associate's degree",
            "Bachelor's degree",
            "Master's degree",
            "Doctoral or professional degree (PhD, JD, MD, etc.)",
            "Other"
        ]
    )

    # Q6. Field of Study
    field_of_study = models.StringField(
        label="What is your primary field of study/profession?",
        choices=[
            "Humanities and Social Sciences",
            "Science, Technology, Engineering, and Mathematics (STEM)",
            "Medical Sciences",
            "Arts / Design / Sports",
            "Business / Law",
            "Other"
        ]
    )

    # Q7. Income
    income = models.StringField(
        label="What is your approximate annual household income?",
        choices=[
            "Less than $25,000",
            "$25,000 to $49,999",
            "$50,000 to $74,999",
            "$75,000 to $99,999",
            "$100,000 to $149,999",
            "$150,000 or more",
            "Prefer not to say"
        ]
    )

    # Q8. Religion
    religion = models.StringField(
        label="Do you identify with a religious group?",
        choices=[
            "Christianity (Protestant, Catholic, etc.)",
            "Judaism",
            "Islam",
            "Other Religion",
            "No Religion (Atheist, Agnostic, or None)",
            "Prefer not to say"
        ]
    )

    # Q9. Marital Status
    marital_status = models.StringField(
        label="What is your marital status?",
        choices=[
            "Single, never married",
            "In a committed relationship",
            "Married",
            "Divorced or separated",
            "Widowed"
        ]
    )

    # Q10. AI Tools Frequency
    ai_use_freq = models.StringField(
        label="How often do you use AI tools (like ChatGPT, Midjourney, etc.) in your daily life?",
        choices=[
            "Rarely (less than once a month)",
            "Occasionally (a few times a month)",
            "Frequently (a few times a week)",
            "Almost every day"
        ],
        widget=widgets.RadioSelect
    )

    # Q11. Attitude towards AI
    ai_attitude = models.StringField(
        label="What is your overall attitude towards AI?",
        choices=[
            "Very negative",
            "Somewhat negative",
            "Neutral",
            "Somewhat positive",
            "Very positive"
        ],
        widget=widgets.RadioSelect
    )

    # Q12. Specialized AI Companion
    ai_companion = models.StringField(
        label="Have you ever used a specialized AI companion app designed specifically for emotional connection, romance, or friendship? (Examples: Replika, Character.ai, Woebot, Loverse)",
        choices=["No", "Yes"],
        widget=widgets.RadioSelect
    )

    # Q13. General AI for Personal Topics
    ai_general_personal = models.StringField(
        label="Have you ever used a general-purpose AI assistant to discuss personal topics (e.g., emotions, relationships, or psychological stress)?",
        choices=[
            "No",
            "Yes, I often use them for emotional support",
            "Yes, but only rarely for this purpose"
        ],
        widget=widgets.RadioSelect
    )

    # --- Conditional Questions (Q14 & Q15) ---
    # 这些问题只有在 Q12="Yes" 或 Q13!="No" 时才显示，所以必须设置 blank=True

    # Q14. Percentage of time
    ai_personal_pct = models.IntegerField(
        min=0, max=100, 
        label="Thinking about your TOTAL usage of AI tools, approximately what percentage of your time is spent discussing personal or emotional topics?",
        blank=True
    )

    # Q15. Topics Frequency (Matrix)
    # 1-7 scale for multiple items
    topic_spouse = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="Relationship with spouse/partner", blank=True)
    topic_family = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="Relationship with parents/family", blank=True)
    topic_friends = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="Friendships", blank=True)
    topic_work = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="Study/Work/Career development", blank=True)
    topic_emotions = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="Personal emotions (e.g., anxiety, sadness)", blank=True)
    topic_health = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="Physical health problems", blank=True)
    
    # Topic Other
    topic_other_freq = models.IntegerField(choices=LIKERT_7, widget=widgets.RadioSelectHorizontal, label="Other", blank=True)
    topic_other_text = models.StringField(label="Please specify other topic:", blank=True)

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
    form_fields = [
        'age', 'gender', 'nationality', 'race', 
        'education', 'field_of_study', 'income', 'religion', 'marital_status',
        'ai_use_freq', 'ai_attitude', 'ai_companion', 'ai_general_personal',
        # Conditional fields:
        'ai_personal_pct', 
        'topic_spouse', 'topic_family', 'topic_friends', 'topic_work', 'topic_emotions', 'topic_health', 
        'topic_other_freq', 'topic_other_text'
    ]
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