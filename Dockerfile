# First stage: Download GeoIP databases using maxmindinc/geoipupdate
FROM ghcr.io/maxmind/geoipupdate:latest as geoipupdate-stage

# Build arguments for geoipupdate configuration
ARG GEOIPUPDATE_ACCOUNT_ID
ARG GEOIPUPDATE_LICENSE_KEY
ARG GEOIPUPDATE_EDITION_IDS
ARG GEOIPUPDATE_FREQUENCY=0

# Set environment variables from build arguments
ENV GEOIPUPDATE_ACCOUNT_ID=${GEOIPUPDATE_ACCOUNT_ID}
ENV GEOIPUPDATE_LICENSE_KEY=${GEOIPUPDATE_LICENSE_KEY}
ENV GEOIPUPDATE_EDITION_IDS=${GEOIPUPDATE_EDITION_IDS}
ENV GEOIPUPDATE_FREQUENCY=${GEOIPUPDATE_FREQUENCY}

# Run the entry script to update the database
RUN /usr/bin/entry.sh

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