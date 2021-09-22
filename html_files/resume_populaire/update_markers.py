import re
from datetime import datetime
import csv

from bs4 import BeautifulSoup

f_html = open("leçon-06.html", 'r', encoding='utf-8')
f_markers = open("Markers_6_3.csv", "r")

reader = csv.DictReader(f_markers, dialect=csv.excel_tab)

soup = BeautifulSoup(f_html, 'html5lib')

row: dict
for row in reader:
    duration: str
    name: str
    name, start, duration, time_format, type, description = row.values()
    hours, minutes, seconds = tuple(map(lambda x: int(x), name.split(':')))
    old_time = datetime(hour=hours, minute=minutes, second=seconds, year=1,
                        month=1, day=1).time()

    if start.count(':') > 1:
        new_time_format = "%H:%M:%S"
    else:
        new_time_format = "%M:%S"

    new_time = datetime.strptime(start.split('.')[0], new_time_format)
    new_time_string = new_time.strftime(new_time_format)
    if old_time.hour > 0:
        old_time_format = "X%H:X%M:%S"
    else:
        old_time_format = "X%M:X%S"
    old_time_string = old_time.strftime(old_time_format).replace('X0', '').replace('X', '')
    print(old_time_string, new_time_string, sep='\t')
    link = soup.find('a', text=old_time_string)
    link["href"] = f"?T={new_time_string}#resume_populaire"
    link.string = new_time_string


