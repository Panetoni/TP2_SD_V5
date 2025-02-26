FROM python:3.9-slim

WORKDIR /app

COPY learner.py .

RUN pip install flask requests

ENV PYTHONUNBUFFERED=1

CMD ["python", "learner.py"]