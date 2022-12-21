FROM python:3.9.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN mkdir /code

RUN python ./download_models.py

COPY ./aqg_api/requirements.txt /code

WORKDIR /code

RUN pip install -r requirements.txt
RUN pip install git+https://github.com/boudinfl/pke.git
RUN pip install gunicorn
RUN python -m spacy download en_core_web_sm

COPY ./aqg_api /code

