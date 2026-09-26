# syntax=docker/dockerfile:1
# IR (incident response) domain image: log analysis, backdoor hunting, timeline.
# GH_PROXY (optional): prefix for github downloads, e.g. https://ghproxy.net/
FROM ctf-base

ARG GH_PROXY=""

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        lnav goaccess chkrootkit rkhunter sysstat acct lsof psmisc \
        libparse-win32registry-perl \
    && rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3013
RUN pip install --no-cache-dir sigma-cli pysigma python-registry

# lynis (audit), RegRipper3.0 (registry), evtx_dump (windows event logs)
RUN set -eux; \
    git clone --depth 1 https://github.com/CISOfy/lynis /opt/lynis; \
    git clone --depth 1 https://github.com/keydet89/RegRipper3.0 /opt/regripper; \
    curl -fsSL "${GH_PROXY}https://github.com/omerbenamram/evtx/releases/download/v0.12.3/evtx_dump-v0.12.3-x86_64-unknown-linux-musl" \
        -o /usr/local/bin/evtx_dump; \
    chmod +x /usr/local/bin/evtx_dump

WORKDIR /ctf
CMD ["/bin/bash"]
