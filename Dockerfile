FROM python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /code
WORKDIR /code

EXPOSE 80
RUN ls
