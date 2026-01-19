# settings.py
import os
from os import environ
import dj_database_url

# Railway 生产环境检测（最稳方案）
PRODUCTION = os.getenv('RAILWAY_ENVIRONMENT_NAME') is not None

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

# 必需的 Django / oTree 配置
ROOT_URLCONF = 'urls'
INSTALLED_APPS = ['otree']

# 数据库配置（自动适配 Railway Postgres / 本地 sqlite）
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3')
}

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(__file__), '_static')

# 生产 / 开发环境通用配置
DEBUG = not PRODUCTION

# Railway / 云部署最稳配置，避免 403
ALLOWED_HOSTS = ['*']
