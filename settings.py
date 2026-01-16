# settings.py
import os
from os import environ

# Railway 生产环境检测
PRODUCTION = os.getenv('ENVIRONMENT') == 'production' or os.getenv('RAILWAY_ENVIRONMENT_NAME') == 'production'

# 基本 oTree 配置
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
    real_world_currency_per_point=0.05,
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

# 设置数据库
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(os.path.dirname(__file__), "db.sqlite3"),
    }
}

# 静态文件配置
STATIC_URL = '/static/'
if PRODUCTION:
    STATIC_ROOT = '/home/gotham/oTree-project/_static'
else:
    STATIC_ROOT = os.path.join(os.path.dirname(__file__), '_static')

# 生产环境配置
if PRODUCTION:
    DEBUG = False
    ALLOWED_HOSTS = [
        'otree-project.railway.app',
        '*.railway.app',
        'gotham.pythonanywhere.com',
        'localhost',
        '127.0.0.1',
    ]
else:
    DEBUG = True
    ALLOWED_HOSTS = ['*']