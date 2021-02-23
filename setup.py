from setuptools import setup

setup(
    name='chkweb',
    version='0.1.2',
    py_modules=['chkweb'],
    url="https://github.com/euribates/chkweb.git",
    install_requires=[
        'click',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'chkweb=chkweb:main',
            'checkweb=chkweb:main',
        ],
    }
)

