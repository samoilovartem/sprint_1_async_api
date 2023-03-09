FROM python:3.10-alpine

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

COPY . /app
WORKDIR /app/
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod +x  /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "main.py"] 
