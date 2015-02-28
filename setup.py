__author__ = 'ethan'
import os
import os.path
from distutils.core import setup
from sys import platform

if platform == "win32":
    import py2exe

    setup(console=['misc_tools.py'])

else:
    myloc = os.getcwd()
    mt_file = os.path.join(myloc, "misc_tools.py")

    from PyInstaller import main as pyinstaller

    pyinstaller.run(pyi_args=[mt_file, '-y'])