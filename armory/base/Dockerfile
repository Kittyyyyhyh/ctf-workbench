# syntax=docker/dockerfile:1
# ctf-workbench base image: shared foundation for all domain images.
# Regional acceleration (optional, set as build args):
#   APT_MIRROR=https://mirrors.tuna.tsinghua.edu.cn/ubuntu
#   PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
FROM ubuntu:24.04

ARG APT_MIRROR=""
ARG PIP_INDEX_URL=""

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TERM=xterm-256color \
    PIP_BREAK_SYSTEM_PACKAGES=1

RUN if [ -n "$APT_MIRROR" ]; then \
        sed -ri "s#https?://(archive|security)\.ubuntu\.com#${APT_MIRROR}#g" \
            /etc/apt/sources.list.d/ubuntu.sources; \
    fi
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential ca-certificates curl wget git file zip unzip xz-utils bzip2 \
        p7zip-full python3 python3-pip python3-venv python3-dev \
        openssh-client netcat-openbsd socat iproute2 iputils-ping dnsutils net-tools \
        jq ripgrep fd-find tmux vim nano less man-db lsb-release gnupg sqlite3 \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/local/bin/python \
    && ln -sf /usr/bin/pip3 /usr/local/bin/pip

# Regional pip index, inherited by all derived images via /etc/pip.conf
RUN if [ -n "$PIP_INDEX_URL" ]; then \
        printf '[global]\nindex-url = %s\n' "$PIP_INDEX_URL" > /etc/pip.conf; \
    fi

WORKDIR /ctf
CMD ["/bin/bash"]
