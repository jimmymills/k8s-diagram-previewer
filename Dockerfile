FROM python:3.9-buster
WORKDIR /project

RUN apt-get update && apt-get install -y graphviz 
RUN curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash

COPY . .

RUN pip install .

WORKDIR /target
ENTRYPOINT ["k8s-diagram"]