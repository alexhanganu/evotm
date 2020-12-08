from os import path, makedirs, environ, sep
from sys import platform

def _get_credentials_home():
    if platform == 'win32':
        home = environ['USERPROFILE']
    else:
        home = environ['HOME']
    credentials_path = path.join(path.dirname(__file__), "credentials_path")
    credentials_home = open(credentials_path).readlines()[0].replace("~",home).replace(sep, '/')
#    print(credentials_home)
    if not path.exists(credentials_home):
        makedirs(credentials_home)
    return credentials_home


