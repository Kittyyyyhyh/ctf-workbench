# syntax=docker/dockerfile:1
# OSINT domain image: username/email/phone recon, DNS, metadata.
# GH_PROXY (optional): prefix for github downloads, e.g. https://ghproxy.net/
FROM ctf-base

ARG GH_PROXY=""

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        whois libimage-exiftool-perl proxychains4 \
    && rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3013
RUN pip install --no-cache-dir \
        maigret holehe dnstwist phonenumbers exifread \
        requests beautifulsoup4 lxml

# sherlock: the PyPI package is an abandoned 2018 release; install from upstream
RUN pip install --no-cache-dir "git+${GH_PROXY}https://github.com/sherlock-project/sherlock.git"

WORKDIR /ctf
CMD ["/bin/bash"]
