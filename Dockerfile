FROM python:3.10-slim

WORKDIR /application

RUN apt update && apt install -y build-essential libpq-dev

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app .

CMD ["streamlit", "run" , "./tagging.py"]