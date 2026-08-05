# "v4-" stacks use our new, more rigorous buildpacks management system. They
# allow you to use multiple buildpacks in a single application, as well as to
# use custom buildpacks.
#
# - `v2-` images work with heroku-import v3.x.
# - `v4-` images work with heroku-import v4.x. (We synced the tags.)

ARG IMPORT_VERSION=v4
ARG HEROKU_STACK=${IMPORT_VERSION}-heroku-20
FROM ghcr.io/renderinc/heroku-app-builder:${HEROKU_STACK} AS builder

# Maxmind Database Update

USER root

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:maxmind/ppa && \
    apt-get update && \
    apt-get install -y libmaxminddb0 libmaxminddb-dev mmdb-bin geoipupdate && \
    mkdir -p /app/geoip

ENV MAXMIND_ACCOUNT_ID ${GEOIPUPDATE_ACCOUNT_ID}
ENV MAXMIND_LICENSE_KEY ${GEOIPUPDATE_LICENSE_KEY}

COPY GeoIP.conf /etc/GeoIP.conf
RUN geoipupdate -v -f /etc/GeoIP.conf -d /app/geoip

# Download ffmpeg

RUN mkdir -p /tmp/ffmpeg && mkdir -p /app/ffmpeg && \
    curl -L 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz' -o /tmp/ffmpeg.tar.xz && \
    tar -xf /tmp/ffmpeg.tar.xz -C /tmp/ffmpeg --strip-components=1 && \
    chmod +x /tmp/ffmpeg/bin/ffmpeg

# Below, please specify any build-time environment variables that you need to
# reference in your build (as called by your buildpacks). If you don't specify
# the arg below, you won't be able to access it in your build. You can also
# specify a default value, as with any Docker `ARG`, if appropriate for your
# use case.

# ARG MY_BUILD_TIME_ENV_VAR
ARG DATABASE_URL
ARG EMAIL_URL

# The FROM statement above refers to an image with the base buildpacks already
# in place. We then run the apply-buildpacks.py script here because, unlike our
# `v2` image, this allows us to expose build-time env vars to your app.
RUN /render/build-scripts/apply-buildpacks.py ${HEROKU_STACK}

# Generate the combined CA bundle at build time using only verified PEM-formatted Russian root/sub certificates
RUN python -c "import os, sys, traceback; \
try: \
    try: \
        import certifi; \
        ca_path = certifi.where(); \
    except ImportError: \
        ca_path = '/etc/ssl/certs/ca-certificates.crt'; \
    d = '/app/tinkoff_merchant/certs'; \
    if not os.path.exists(d): \
        d = os.path.abspath('tinkoff_merchant/certs'); \
    f_out = os.path.join(d, 'combined_ca.pem'); \
    default_certs = open(ca_path, 'r', encoding='utf-8').read(); \
    custom_certs = []; \
    if os.path.exists(d): \
        for f in os.listdir(d): \
            if (f.endswith('.pem') or f.endswith('.crt')) and f != 'combined_ca.pem': \
                with open(os.path.join(d, f), 'r', encoding='utf-8', errors='ignore') as file: \
                    content = file.read(); \
                    if '-----BEGIN CERTIFICATE-----' in content: \
                        custom_certs.append(content.strip()); \
    open(f_out, 'w', encoding='utf-8').write(default_certs + '\n\n' + '\n\n'.join(custom_certs)); \
    print('Generated Docker CA bundle successfully at:', f_out); \
except Exception as e: \
    traceback.print_exc(); \
    sys.exit(1);"

# We strongly recommend that you package a Procfile with your application, but
# if you don't, we'll try to guess one for you. If this is incorrect, please
# add a Procfile that tells us what you need us to run.
RUN if [[ -f /app/Procfile ]]; then \
  /render/build-scripts/create-process-types "/app/Procfile"; \
fi;

# For running the app, we use a clean base image and also one without Ubuntu development packages
# https://devcenter.heroku.com/articles/heroku-20-stack#heroku-20-docker-image
FROM ghcr.io/renderinc/heroku-app-runner:${HEROKU_STACK} AS runner

# Here we copy your build artifacts from the build image to the runner so that
# the image that we deploy to Render is smaller and, therefore, can start up
# faster.
COPY --from=builder --chown=1000:1000 /render /render/
COPY --from=builder --chown=1000:1000 /app /app/
COPY --from=builder --chown=1000:1000 /tmp/ffmpeg/bin /app/ffmpeg/
ENV PATH="$PATH:/app/ffmpeg"

# Here we're switching to a non-root user in the container to remove some categories
# of container-escape attack.
USER 1000:1000
WORKDIR /app

# This sources all /app/.profile.d/*.sh files before process start.
# These are created by buildpacks, and you probably don't have to worry about this.
# https://devcenter.heroku.com/articles/buildpack-api#profile-d-scripts
ENTRYPOINT [ "/render/setup-env" ]

# 3. By default, we run the 'web' process type defined in the app's Procfile
# You may override the process type that is run by replacing 'web' with another
# process type name in the CMD line below. That process type must have been
# defined in the app's Procfile during build.
CMD [ "/render/process/web" ]
