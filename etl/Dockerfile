FROM python:3.11

RUN apt-get update

COPY . /app
WORKDIR /app/
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "main.py"] 
