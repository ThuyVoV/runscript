import subprocess
import sys
from .view_helper import get_temp
from datetime import datetime


def run_task(*args):
    print(args)
    # path = args[0][0]
    # arguments = args[0][1]
    # ext = args[0][2]
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


    path = args[0]
    arguments = args[1]
    ext = args[2]
    print('path', path)
    print('arg', arguments)
    print('ext', ext)
    print("date and time =", dt_string)

    t = open(get_temp(), 'w')

    if ext == 'sh':
        subprocess.call(['sh', path] + arguments, text=True, stdout=t)
    elif ext == 'py':
        subprocess.run([sys.executable, path] + arguments, text=True, stdout=t)
    t.close()
