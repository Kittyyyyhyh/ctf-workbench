# syntax=docker/dockerfile:1
# AI domain image: LLM attack tooling, OCR, prompt-injection payload library.
# NOTE: the LLM runtime itself is NOT baked here (models are runtime-pulled
# multi-GB artifacts) — see armory/scenarios/ai-injection for the ollama setup.
# GH_PROXY (optional): prefix for github downloads, e.g. https://ghproxy.net/
FROM ctf-base

ARG GH_PROXY=""

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim \
    && rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3013
RUN pip install --no-cache-dir \
        openai anthropic httpx requests pillow pytesseract beautifulsoup4

# curated prompt-injection corpus for offline reference
COPY payloads/ /opt/payloads/

# heavy LLM eval frameworks are optional (torch-sized):
#   docker compose build ai  with  INSTALL_GARAK=1
ARG INSTALL_GARAK="0"
RUN if [ "$INSTALL_GARAK" = "1" ]; then pip install --no-cache-dir garak; fi

WORKDIR /ctf
CMD ["/bin/bash"]
