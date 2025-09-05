# syntax=docker.io/docker/dockerfile:1.16-labs@sha256:bb5e2b225985193779991f3256d1901a0b3e6a0b284c7bffa0972064f4a6d458

# This Dockerfile is a modified copy of the latest Element-Web dockerfile,
# with the additional builder step of using the CLI to generate the patched
# element-web instance

FROM python:3.13.5-alpine AS cli_builder

WORKDIR /app

# Copy the CLI files
COPY --exclude=__pycache__ \
    --exclude=.cache \
    ./cli /app/cli
COPY make.py /app/make.py
COPY build_config.yml /app/build_config.yml
COPY --exclude=local \
    --exclude=config.json \
    --exclude=.env \
    projects/element-web /app/projects/element-web

# Install dependencies
RUN apk add patch
RUN python3 -m venv --upgrade-deps /venv
ENV PATH=/venv/bin:$PATH
RUN pip install --no-compile --no-cache-dir -r /app/cli/requirements.txt

# Generate the files for element-web
RUN python make.py init element-web -y --link-mode copy


# Element-web -----------

# Builder
FROM --platform=$BUILDPLATFORM node:22-bullseye@sha256:f16d8e8af67bb6361231e932b8b3e7afa040cbfed181719a450b02c3821b26c1 AS builder


RUN yarn config set strict-ssl false -g

WORKDIR /src

# Set the VERSION environment value; should be built in automatically in CI/CD
ARG CICDVERSION=0.0.0

# Copy from the cli_builder instead, and skip any JS_SDK links
COPY --from=cli_builder --exclude=docker /app/projects/element-web/local /src
RUN yarn --network-timeout=200000 install
RUN VERSION=${CICDVERSION} yarn build

# Copy the config now so that we don't create another layer in the app image
RUN cp /src/config.sample.json /src/webapp/config.json

# App
FROM nginxinc/nginx-unprivileged:alpine-slim@sha256:66e34aa81c2faf290ea4e4c28a490f2b35a07478265a2d5994c8637506045eee

# Need root user to install packages & manipulate the usr directory
USER root

# Install jq and moreutils for sponge, both used by our entrypoints
RUN apk add --no-cache jq moreutils

COPY --from=builder /src/webapp /app

# Override default nginx config. Templates in `/etc/nginx/templates` are passed
# through `envsubst` by the nginx docker image entry point.
COPY --from=cli_builder /app/projects/element-web/local/docker/nginx-templates/* /etc/nginx/templates/
COPY --from=cli_builder /app/projects/element-web/local/docker/docker-entrypoint.d/* /docker-entrypoint.d/

# Copy additional scripts and grant permissions
COPY ./projects/element-web/scripts/replace_vars.sh /scripts/replace_vars.sh
COPY ./projects/element-web/scripts/start.sh /docker-entrypoint.d/start.sh

# Fix script permissions
RUN chmod +x /docker-entrypoint.d/*.sh /scripts/*.sh \
  && chown -R 101:101 /app /etc/nginx /docker-entrypoint.d /scripts \
  && rm -rf /usr/share/nginx/html \
  && ln -s /app /usr/share/nginx/html

# Switch to the non-root nginx user
USER nginx

# TODO: We previously set user as nginx but we need permissions to run scripts

# HTTP listen port
ENV ELEMENT_WEB_PORT=8080

HEALTHCHECK --start-period=5s CMD wget -q --spider http://localhost:$ELEMENT_WEB_PORT/config.json
