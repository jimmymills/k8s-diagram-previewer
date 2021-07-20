FROM python:3.9-buster
WORKDIR /target

COPY . .

RUN apt-get update && apt-get install -y graphviz && pip install .

ENTRYPOINT ["k8s-diagram", "."]