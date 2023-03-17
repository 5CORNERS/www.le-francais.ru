#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

import os
import sys

try:
    from dotenv import load_dotenv
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'le_francais.settings.dev')
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except ModuleNotFoundError:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.getenv('DJANGO_SETTINGS_MODULE'))

sys.tracebacklimit = 30000

if __name__ == "__main__":


    from django.core.management import execute_from_command_line


    execute_from_command_line(sys.argv)
