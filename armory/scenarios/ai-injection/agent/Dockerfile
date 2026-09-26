# syntax=docker/dockerfile:1
# 可被注入攻击的 agent 应用（练习场景）
FROM ctf-base

# hadolint ignore=DL3013
RUN pip install --no-cache-dir flask requests

WORKDIR /app
COPY bootstrap.py app.py /app/

CMD ["python3", "/app/bootstrap.py"]
