#!/usr/bin/python

from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files':1}},
    windows = [{'script': 'kindledecrypt.py'}],
    zipfile = None,
)
