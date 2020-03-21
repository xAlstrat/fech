from .base import *

DEBUG = False

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['localhost', '35.153.184.146']

try:
    from .local import *
except ImportError:
    pass

print('Running as production')