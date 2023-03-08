FROM python:3.11-alpine

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

COPY . /app
WORKDIR /app/
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod +x  /app/entrypoint.dev.sh
ENTRYPOINT ["/app/entrypoint.dev.sh"]

CMD ["python", "main.py"] 
