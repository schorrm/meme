from setuptools import setup, find_packages

setup(
    name='meme',
    version='0.1.0',
    description='Standard Meme Compiler v. 0.1',
    author='Lior Ramati & Moshe Schorr',
    url='https://github.com/schorrm/meme',
    packages=find_packages(include=['src', 'src/*']),
    include_package_data=True,
    license='LICENSE',
    install_requires=[
        'Pillow>=6.2.0',
        'lark-parser'
    ],
    entry_points={
        'console_scripts': ['meme=src.console:main']
    },
)
