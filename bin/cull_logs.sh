#!/bin/bash
/app/.heroku/python/bin/python3 /app/manage.py clearsessions
/app/.heroku/python/bin/python3 /app/manage.py cull_logs 30