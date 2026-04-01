FROM python:3.13.12-slim

WORKDIR /opt/chatbot
COPY . /opt/chatbot/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "src.main", "--autorun"]