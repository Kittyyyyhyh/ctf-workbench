# syntax=docker/dockerfile:1
# Web domain image: scanners, fuzzers, deserialization playgrounds.
# GH_PROXY (optional): prefix for github downloads, e.g. https://ghproxy.net/
FROM ctf-base

ARG GH_PROXY=""

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nmap whatweb php-cli php-curl php-mysql php-xml \
        libffi-dev libssl-dev libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3013
RUN pip install --no-cache-dir \
        requests httpx aiohttp flask jinja2 beautifulsoup4 lxml pyyaml paramiko \
        dirsearch sqlmap arjun wafw00f

# Go-based fuzzers/scanners from GitHub releases
RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    curl -fsSL "${GH_PROXY}https://github.com/ffuf/ffuf/releases/download/v2.1.0/ffuf_2.1.0_linux_${arch}.tar.gz" -o /tmp/ffuf.tgz; \
    tar -xzf /tmp/ffuf.tgz -C /usr/local/bin ffuf; \
    curl -fsSL "${GH_PROXY}https://github.com/OJ/gobuster/releases/download/v3.6.0/gobuster_3.6.0_linux_${arch}.tar.gz" -o /tmp/gobuster.tgz; \
    tar -xzf /tmp/gobuster.tgz -C /usr/local/bin gobuster; \
    curl -fsSL "${GH_PROXY}https://github.com/projectdiscovery/nuclei/releases/download/v3.3.9/nuclei_3.3.9_linux_${arch}.zip" -o /tmp/nuclei.zip; \
    unzip -o /tmp/nuclei.zip -d /usr/local/bin nuclei; \
    curl -fsSL "${GH_PROXY}https://github.com/projectdiscovery/httpx/releases/download/v1.6.9/httpx_1.6.9_linux_${arch}.zip" -o /tmp/httpx.zip; \
    unzip -o /tmp/httpx.zip -d /usr/local/bin httpx; \
    chmod +x /usr/local/bin/ffuf /usr/local/bin/gobuster /usr/local/bin/nuclei /usr/local/bin/httpx; \
    rm -f /tmp/ffuf.tgz /tmp/gobuster.tgz /tmp/nuclei.zip /tmp/httpx.zip

WORKDIR /ctf
CMD ["/bin/bash"]
