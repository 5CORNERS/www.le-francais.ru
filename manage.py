#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

import os
import sys

from dotenv import load_dotenv

sys.tracebacklimit = 30000

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "le_francais.settings.dev")

    from django.core.management import execute_from_command_line

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    execute_from_command_line(sys.argv)
