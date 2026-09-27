# syntax=docker/dockerfile:1
# Forensics domain image: stego, memory/disk, pcap, document & file carving.
# GH_PROXY (optional): prefix for github downloads, e.g. https://ghproxy.net/
FROM ctf-base

ARG GH_PROXY=""

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libimage-exiftool-perl binwalk foremost testdisk sleuthkit \
        steghide outguess tshark yara qpdf poppler-utils pv unar ruby-full \
        zbar-tools imagemagick sox libsox-fmt-all sqlcipher fcrackzip \
        tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim \
    && rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3013
RUN pip install --no-cache-dir \
        volatility3 python-magic yara-python oletools pefile scapy pyshark \
        pillow qrcode pytesseract scapy pyshark

RUN gem install --no-document zsteg

# evtx_dump: windows event log -> xml
RUN set -eux; \
    curl -fsSL "${GH_PROXY}https://github.com/omerbenamram/evtx/releases/download/v0.12.3/evtx_dump-v0.12.3-x86_64-unknown-linux-musl" \
        -o /usr/local/bin/evtx_dump; \
    chmod +x /usr/local/bin/evtx_dump

# miskit: one-shot misc attacks (CRC brute/pngfix/USB-HID/TTL/nested base/
# steghide brute), see armory/forensics/miskit/ (idea provenance: Des-CTF-Knowledge, MIT)
COPY miskit/ /opt/miskit/
RUN chmod +x /opt/miskit/miskit.py \
    && ln -sf /opt/miskit/miskit.py /usr/local/bin/miskit

WORKDIR /ctf
CMD ["/bin/bash"]
