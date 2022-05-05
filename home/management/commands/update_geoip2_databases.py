import os
from pathlib import Path
from urllib.request import urlretrieve

from django.core.management import BaseCommand


def download(url, to):
    Path(to).mkdir(parents=True, exist_ok=True)
    try:
        urlretrieve(url, to)
        return True
    except:
        return False


class Command(BaseCommand):
    def handle(self, *args, **options):
        if download(
            os.environ.get('GEOIP_CITY_DOWNLOAD_LINK'),
            f'{os.environ.get("GEOIP_GEOLITE2_PATH")}/{os.environ.get("GEOIP_GEOLITE2_CITY_FILENAME")}'
        ) and download(
            os.environ.get('GEOIP_COUNTRY_DOWNLOAD_LINK'),
            f'{os.environ.get("GEOIP_GEOLITE2_PATH")}/{os.environ.get("GEOIP_GEOLITE2_COUNTRY_FILENAME")}'
        ):
            print("Done")
        else:
            print('Error!')
