#!/usr/bin/env python3

from setuptools import setup, find_packages

# We want to restrict newer versions while we deal with upstream breaking changes.
discordpy_version = '==0.10.0'

# TODO read README(.rst? .md looks bad on pypi) for long_description.
#      Could use pandoc, but the end user shouldn't need to do this in setup.
#      Alt. could have package-specific description. More error-prone though.

setup(
    # More permanent entries
    name='CrabBot',
    author='TAOTheCrab',
    url='https://github.com/TAOTheCrab/CrabBot',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License'
        'Programming Language :: Python :: 3.5'
    ],

    # Entries likely to be modified
    description='A simple Discord bot',
    version='0.0.1',  # TODO figure out a version scheme. Ensure this gets updated.

    packages=find_packages(),  # A little lazy

    install_requires=[
        'discord.py{}'.format(discordpy_version)
    ],
    extras_require={
        'voice': [
            'discord.py[voice]{}'.format(discordpy_version),
            'youtube_dl'
        ]
    }
)
