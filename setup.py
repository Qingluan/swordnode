from setuptools import setup, find_packages
from setuptools.command.install import install
import os, sys
import time

DB_PATH = os.path.expanduser("~/.config/SwordNode/")
DB_PATH_C = os.path.expanduser("~/.config/")
PLUGIN_PATH = os.path.join(DB_PATH, 'plugins')
TEST_MODULES_ROOT = os.path.expanduser("~/.config/SwordNode/plugins/Plugins")
E = os.path.exists
SHOME = os.path.expanduser("~/.config/SwordNode")
J = os.path.join

class MyInstall(install):
    def run(self):
        install.run(self)

        HandleDir = os.path.join(os.path.dirname(__file__), "handlers")
        if not E(SHOME):
            os.mkdir(SHOME)


        if not E(PLUGIN_PATH):
            os.mkdir(os.path.join(SHOME, 'plugins'))
            os.mkdir(os.path.join(PLUGIN_PATH, 'Plugins'))
            with open(J(J(PLUGIN_PATH, 'Plugins'), '__init__.py'), 'w') as fp: pass


        if os.path.exists(HandleDir):
            print("\n\n\n--- < install phantomjs > -------\n")
            time.sleep(1)

        
        # os.rename(os.path.join(os.path.dirname(__file__), "res/phantomjs"), "/usr/local/bin/phantomjs")

        os.popen("cd %s && git init " % TEST_MODULES_ROOT)
        os.popen("cd %s && git remote add origin https://github.com/Qingluan/x-plugins.git"  % TEST_MODULES_ROOT)

        for file in os.listdir("handlers"):
            if file.endswith(".raw"):
                src = os.path.join("handlers", file)
                des = os.path.join(TEST_MODULES_ROOT, file.rsplit("raw", 1)[0] + "py")
                
            elif file.endswith('.bash'):
                src = os.path.join('handlers', file)
                des = os.path.join(TEST_MODULES_ROOT, file)

            os.popen("cp -v {} {} ".format(src, des)).read()


setup(name='x-mroy-1052',
    version='0.0.1',
    description='a anayzer package',
    url='https://github.com/Qingluan/.git',
    cmdclass={"install": MyInstall},
    author='Qing luan',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=[ 'mroylib-min','x-mroy-1045', 'qtornado'],
    entry_points={
        'console_scripts': ['x-neid=swordserver.main:main']
    },

)
