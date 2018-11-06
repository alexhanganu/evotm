#!/usr/bin/python3
#updated 2018-03-18

from os import path
from sys import platform

PATHapp = getcwd().replace(path.sep, '/')+'/tm/'


def setup():
    from os import environ, system

    try:
        import pandas
    except ImportError:
        system('pip3 install pandas')
    system('pip3 install oauth2client')
    system('pip3 install --upgrade google-api-python-client')
    if platform == 'darwin' or platform == 'linux' or platform == 'linux2':
       PATH_Desktop = path.expanduser('~')+'/Desktop/'
    if platform == 'win32':
        PATH_Desktop=((environ['USERPROFILE']).replace('\\','/')+'/Desktop/')
        with open(PATH_Desktop+'run_tm.bat','w') as f:
            f.write('cd '+PATHapp+'\n'+'start pythonw tm.pyw')
