"""
Django settings for code_pass project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6r!peo8vc#148^$t6tynxo-9fd00wi2frc2x-3--w=5o&qxap4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# 设置所有人访问
ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'CodePass',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]
# 根urls路径
ROOT_URLCONF = 'code_pass.urls'

# 模板路径1
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 注册template模板的位置
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 部署需要用
WSGI_APPLICATION = 'code_pass.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'codedupldetec',
        'USER': 'root',
        'PASSWORD': '2031410',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# 配置缓存
CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
# 认证密码验证器
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
# 网站的语言
LANGUAGE_CODE = 'zh-hans'
# 亚洲上海的时钟
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

# 关闭Django的时区，防止用filer过滤model对象集的时候有问题。
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

# 图片使用
STATIC_URL = '/static/'
# 普通文件使用 js css 在系统中进行注册
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static/axf')
# ]

# # 上传压缩文件目录
UPLOAD_FILE_DIR = os.path.join(BASE_DIR, r'static\CodePass\file\zip_file')
# 上传图片文件的目录‘
UPLOAD_IMG_FILE_DIR = os.path.join(BASE_DIR, r'static\CodePass\file\img_file')
# 上传公告文件的目录
UPLOAD_NOTICE_FILE_DIR = os.path.join(BASE_DIR, r'static\CodePass\file\notice_file')
## 临时文件目录
TEMP_FILE_DIR = os.path.join(BASE_DIR, r'static\CodePass\file\temp_file')
# 解压文件目录
UPLOAD_UNZIP_FILE_DIR = os.path.join(BASE_DIR, r'static\CodePass\file\unzip_file')

FONT_PATH = os.path.join(BASE_DIR, 'static/fonts/ADOBEARABIC-BOLD.OTF')
# jar包的位置
JAR_PATH = os.path.join(BASE_DIR, 'CodePass/lib/ASTExtractor-0.4.jar')
# jar包的属性文件位置
PROPERTY_FILE_PATH = os.path.join(BASE_DIR, 'CodePass/setting/ASTExtractor.properties')

# Unrar.exe的位置
UNRAR_PATH = os.path.join(BASE_DIR, 'CodePass/lib/UnRAR.exe')
# 抄袭判定模型的位置
PREDICT_MODEL = os.path.join(BASE_DIR,'CodePass/lib/VotingClassifier.pkl')

# 跨域配置
# 是否允许携带cookie
CORS_ALLOW_CREDENTIALS = True
# 允许所有源访问
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ()

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)
