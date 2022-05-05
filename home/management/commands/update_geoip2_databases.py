import os
from pathlib import Path
from urllib.request import urlretrieve

from django.core.management import BaseCommand


def download(url, to, filename):
    os.makedirs(to, exist_ok=True)
    try:
        urlretrieve(url, f'{to}/{filename}')
        return True
    except Exception as e:
        print(e)
        return False


class Command(BaseCommand):
    def handle(self, *args, **options):
        if download(
            os.environ.get('GEOIP_CITY_DOWNLOAD_LINK'),
            os.environ.get("GEOIP_GEOLITE2_PATH"),
            os.environ.get('GEOIP_GEOLITE2_CITY_FILENAME')
        ) and download(
            os.environ.get('GEOIP_COUNTRY_DOWNLOAD_LINK'),
            os.environ.get("GEOIP_GEOLITE2_PATH"),
            os.environ.get("GEOIP_GEOLITE2_COUNTRY_FILENAME")
        ):
            print("Done")
        else:
            print('Error!')
