import os
from os import environ

# 生产环境检测
PRODUCTION = os.getenv("RAILWAY_ENVIRONMENT_NAME") == "production"

# oTree session 配置
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

# Django 配置
ROOT_URLCONF = 'urls'
INSTALLED_APPS = ['otree']

# 数据库配置
if "DATABASE_URL" in environ:
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.config(conn_max_age=600)
    }
else:
    # SQLite 本地备用
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(os.path.dirname(__file__), "db.sqlite3"),
        }
    }

# 静态文件
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(__file__), "_static")

# 生产环境设置
DEBUG = not PRODUCTION
ALLOWED_HOSTS = [
    "*",  # Railway 自动生成域名
]
