# settings.py
from os import environ

SESSION_CONFIGS = [
    dict(
        name='materials_experiment',
        display_name="Interesting Experiment",
        num_demo_participants=1,
        app_sequence=['app_intro', 'app_chat', 'app_games', 'app_survey'],
        participation_fee=4.00,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.05,  # 20 tokens (points) = $1
    participation_fee=4.00,
    doc="",
)

LANGUAGE_CODE = 'en'

REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True
POINTS_CUSTOM_NAME = 'tokens'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', 'demo')

DEMO_PAGE_INTRO_HTML = ""

SECRET_KEY = environ.get('OTREE_SECRET_KEY', 'dev-secret-key')

INSTALLED_APPS = ['otree']