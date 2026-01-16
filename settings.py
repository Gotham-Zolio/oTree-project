# settings.py
import os
from os import environ

# Railway 生产环境检测
PRODUCTION = os.getenv('ENVIRONMENT') == 'production' or os.getenv('RAILWAY_ENVIRONMENT_NAME') == 'production'

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

ROOT_URLCONF = 'urls'

# ==================== Railway 生产环境配置 ====================
if PRODUCTION:
    DEBUG = False
    # 允许 Railway 域名和自定义域名访问
    ALLOWED_HOSTS = [
        'otree-project.railway.app',
        '*.railway.app',
        'localhost',
        '127.0.0.1',
    ]
    # 使用静态文件存储 - 使用绝对路径确保在 WSGI 环境中能正确找到
    STATIC_ROOT = '/home/gotham/oTree-project/_static'
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # 开发环境
    DEBUG = True
    ALLOWED_HOSTS = ['*']