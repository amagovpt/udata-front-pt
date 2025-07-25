##########################################
# Dockerfile for udata
##########################################

#FROM udata/system
FROM udata/system:py3.11

# Optionnal build arguments
ARG REVISION="N/A"
ARG CREATED="Undefined"

# OCI annotations
# See: https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL "org.opencontainers.image.title"="udata all-in-one"
LABEL "org.opencontainers.image.description"="udata with all known plugins and themes"
LABEL "org.opencontainers.image.authors"="Open Data Team"
LABEL "org.opencontainers.image.sources"="https://github.com/opendatateam/docker-udata"
LABEL "org.opencontainers.image.revision"=$REVISION
LABEL "org.opencontainers.image.created"=$CREATED

RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list \
    && sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    # uWSGI rooting features
    libpcre3-dev \
    mime-support \
    # xmlsec1 package
    libxmlsec1 libxmlsec1-dev xmlsec1\
    # Clean up
    && apt-get autoremove\
    && apt-get clean\
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install udata and all known plugins
COPY ./requirements/install.pip /tmp/requirements/install.pip
COPY requirements.pip /tmp/requirements.pip
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.pip && pip check || pip install -r /tmp/requirements.pip
RUN rm -r /root/.cache

# Be used with healthcheck
RUN apt-get update && apt-get install -y netcat

# Copy udata configuration and setup
RUN mkdir -p /udata/fs /src

COPY udata.cfg entrypoint.sh /udata/
COPY uwsgi/*.ini /udata/uwsgi/

# Change to the working directory
WORKDIR /udata

VOLUME /udata/fs

ENV UDATA_SETTINGS /udata/udata.cfg

EXPOSE 7000

ENTRYPOINT ["/udata/entrypoint.sh"]
CMD ["uwsgi"]