import os
import sys

# 设置工作目录
project_path = '/home/gotham/oTree-project'
os.chdir(project_path)

# 添加虚拟环境的 site-packages 到 Python 路径
venv_site_packages = '/home/gotham/.virtualenvs/otree_env_py312/lib/python3.12/site-packages'
if venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# 添加项目目录到 Python 路径
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# 设置 PRODUCTION 环境变量
os.environ['ENVIRONMENT'] = 'production'

# 设置 Django 设置模块
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# 导入 WSGI 应用
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()