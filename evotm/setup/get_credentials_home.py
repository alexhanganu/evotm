from os import path, makedirs, environ, sep
from sys import platform

def _get_credentials_home():
    if platform == 'win32':
        home = environ['USERPROFILE']
    else:
        home = environ['HOME']
    try:
        from setup.credentials_path import credentials_home
        credentials_home = credentials_home.replace("~", home).replace(sep, '/')
        if not path.exists(credentials_home):
            makedirs(credentials_home)
    except Exception as e:
        print(e, 'credentials are missing')
        credentials_home = ''
    return credentials_home


