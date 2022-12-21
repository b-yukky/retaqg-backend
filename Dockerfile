FROM python:3.9.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1


RUN mkdir /code

COPY download_models.py /code
COPY ./aqg_api/requirements.txt /code
WORKDIR /code
RUN pip install -r requirements.txt

COPY ./aqg_api /code

RUN pip install git+https://github.com/boudinfl/pke.git
RUN python -m spacy download en_core_web_sm

RUN python download_models.py
