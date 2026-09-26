# syntax=docker/dockerfile:1
# Crypto domain image: number theory, factorization, classic & lattice tooling.
# GH_PROXY (optional): prefix for github downloads, e.g. https://ghproxy.net/
# INSTALL_SAGE=1 adds SageMath via conda-forge (~4GB extra, needs disk headroom);
# the slim default covers factorization/RSA/hash tooling plus sympy/gmpy2/z3.
FROM ctf-base

ARG GH_PROXY=""
ARG INSTALL_SAGE="0"

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        hashcat john pari-gp bc libecm1 \
    && rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3013
RUN pip install --no-cache-dir \
        pycryptodome gmpy2 sympy factordb-python z3-solver \
        gmalg gmssl

# yafu (integer factorization) as a single static binary
RUN set -eux; \
    curl -fsSL "${GH_PROXY}https://github.com/bbuhrow/yafu/releases/download/v3.1.9/yafu-linux-avx2" \
        -o /usr/local/bin/yafu; \
    chmod +x /usr/local/bin/yafu

# mathkit: one-shot CTF math attacks (factor/cuberoot/wiener/fermat/commonmod/
# hastad/dlog/lll), see armory/crypto/mathkit/
COPY mathkit/ /opt/mathkit/
ENV PATH="/opt/mathkit:${PATH}"
RUN ln -sf /opt/mathkit/mathkit.py /usr/local/bin/mathkit

# RsaCtfTool (RSA multi-attack toolkit); upstream is a pyproject package now,
# so install it for a stable `RsaCtfTool` entrypoint
RUN set -eux; \
    git clone --depth 1 https://github.com/RsaCtfTool/RsaCtfTool /opt/RsaCtfTool; \
    pip install --no-cache-dir /opt/RsaCtfTool

# SageMath: the heavy optional layer, via conda-forge (apt no longer ships it
# on ubuntu 24.04). micromamba is a single static binary; the "latest" URL is
# used on purpose so the build tracks micromamba releases without pinning.
ENV MAMBA_ROOT_PREFIX=/opt/micromamba
RUN if [ "$INSTALL_SAGE" = "1" ]; then \
        curl -fsSL "${GH_PROXY}https://github.com/mamba-org/micromamba-releases/releases/latest/download/micromamba-linux-64" \
            -o /usr/local/bin/micromamba \
        && chmod +x /usr/local/bin/micromamba \
        && micromamba create -y -p /opt/sage -c conda-forge sage \
        && ln -s /opt/sage/bin/sage /usr/local/bin/sage; \
    fi

WORKDIR /ctf
CMD ["/bin/bash"]
