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

# 允许所有主机访问，或根据需要自定义
ALLOWED_HOSTS = ['*']

# 静态文件收集目录
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, '_static')

# 数据库配置，优先使用PostgreSQL（推荐Railway部署时设置DATABASE_URL环境变量）
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}')
}

DEMO_PAGE_INTRO_HTML = ""

SECRET_KEY = environ.get('OTREE_SECRET_KEY', 'dev-secret-key')

INSTALLED_APPS = ['otree']