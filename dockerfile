FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY /app .

EXPOSE 5000
CMD ["flask", "--app", "app.py", "run", "--host=0.0.0.0"]