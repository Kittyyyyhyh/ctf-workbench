# syntax=docker/dockerfile:1
# Reverse domain image: decompilers, disassemblers, dynamic analysis, android.
# GH_PROXY (optional): prefix for github downloads, e.g. https://ghproxy.net/
FROM ctf-base

ARG GH_PROXY=""

# JDK 21 is required by Ghidra 12.x; apktool shares it
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-21-jdk-headless radare2 \
    && rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3013
RUN pip install --no-cache-dir \
        frida-tools androguard capstone unicorn keystone-engine pyelftools

# Ghidra (headless decompiler) + apktool
RUN set -eux; \
    curl -fsSL "${GH_PROXY}https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.4_build/ghidra_12.1.4_PUBLIC_20260921.zip" -o /tmp/ghidra.zip; \
    unzip -q /tmp/ghidra.zip -d /opt; \
    mv /opt/ghidra_12.1.4_PUBLIC /opt/ghidra; \
    ln -s /opt/ghidra/support/analyzeHeadless /usr/local/bin/analyzeHeadless; \
    curl -fsSL "${GH_PROXY}https://github.com/iBotPeaches/Apktool/releases/download/v3.0.3/apktool_3.0.3.jar" -o /opt/apktool.jar; \
    printf '#!/bin/sh\nexec java -jar /opt/apktool.jar "$@"\n' > /usr/local/bin/apktool; \
    chmod +x /usr/local/bin/apktool; \
    rm -f /tmp/ghidra.zip

WORKDIR /ctf
CMD ["/bin/bash"]
