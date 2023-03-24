FROM python:3-alpine AS builder

WORKDIR /app

RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Stage 2
FROM python:3-alpine AS runner

WORKDIR /app

COPY --from=builder /app/venv venv
COPY main.py /app/main.py
COPY src ./src

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV FLASK_APP=app/main.py

EXPOSE 8000

CMD [ "uvicorn", "--host", "0.0.0.0", "main:app" ]
