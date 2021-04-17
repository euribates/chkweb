from pathlib import Path
from setuptools import setup


setup(
    name='chkweb',
    version='0.1.5',
    python_requires='>=3.7',
    py_modules=['chkweb'],
    author='Juan Ignacio Rodríguez de León',
    author_email='euribates@gmail.com',
    license='GNU v.3',
    url="https://github.com/euribates/chkweb.git",
    description="A very simple web crawler and checker",
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    install_requires=[
        'fire',
        'prettyconf',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'chkweb=chkweb:main',
        ],
    }
)
