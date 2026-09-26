# syntax=docker/dockerfile:1
# Pwn domain image: exploitation toolchain, multi-arch debugging, gadget tools.
# GH_PROXY (optional): prefix for github downloads, e.g. https://ghproxy.net/
FROM ctf-base

ARG GH_PROXY=""

# i386 runtime for 32-bit challenges; SYS_PTRACE is granted at runtime by the ctf CLI
# hadolint ignore=DL3008
RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gdb gdb-multiarch gcc g++ make cmake libc6-dev \
        libc6:i386 libstdc++6:i386 zlib1g:i386 \
        patchelf strace ltrace binutils ruby-full \
    && rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3013
RUN pip install --no-cache-dir \
        pwntools ROPgadget ropper capstone unicorn keystone-engine pyelftools z3-solver

RUN gem install --no-document one_gadget seccomp-tools \
    && curl -fsSL "${GH_PROXY}https://raw.githubusercontent.com/hugsy/gef/main/gef.py" \
        -o /root/gef.py \
    && echo "source /root/gef.py" >> /root/.gdbinit

# pwntools runs non-interactive inside `ctf exec`; libcdb queries libc.rip for matches
ENV PWNLIB_NOTERM=1

WORKDIR /ctf
CMD ["/bin/bash"]
