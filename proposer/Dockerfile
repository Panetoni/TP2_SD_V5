FROM python:3.9-slim

WORKDIR /app

COPY proposer.py .

RUN pip install flask requests

ENV PYTHONUNBUFFERED=1

CMD ["python", "proposer.py"]