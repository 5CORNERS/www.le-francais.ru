# First stage: Download GeoIP databases using maxmindinc/geoipupdate
FROM maxmindinc/geoipupdate as geoipupdate-stage

COPY ./GeoIP.conf /usr/local/etc/GeoIP.conf
RUN geoipupdate --verbose

# Second stage: Runtime application
FROM python:3.7

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

COPY --from=geoipupdate-stage /usr/share/GeoIP /usr/src/app/geoip

# Install dependencies
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install django-session-header --no-dependencies --no-cache-dir

# Copy app to workdir
COPY . /usr/src/app

# Collect static files
RUN python manage.py collectstatic --noinput

# Gunicorn
CMD ["gunicorn", "le_francais.wsgi", "--bind", "0.0.0.0:8000"]