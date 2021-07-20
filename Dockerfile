FROM python:3.9-buster

WORKDIR /code

COPY ./requirements.txt ./

RUN apt-get update && apt-get install -y graphviz && pip install -r requirements.txt

ENTRYPOINT ["python", "diagram.py"]