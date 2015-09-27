from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*!4%+fcwkmfbarpeb-ffce)m7^fb%^g+*988o%enep4dl%_91t'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'chefwhale.email@gmail.com'
EMAIL_HOST_PASSWORD = 'ofhhzetprzjbfbev'
DEFAULT_FROM_EMAIL = 'chefwhale.email@gmail.com'
SERVER_EMAIL = 'chefwhale.email@gmail.com'

try:
    from .local import *
except ImportError:
    pass
