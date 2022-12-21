FROM python:3.9.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN mkdir /code

COPY ./aqg_api/requirements.txt /code
WORKDIR /code
RUN pip install -r requirements.txt

COPY ./aqg_api /code

RUN pip install git+https://github.com/boudinfl/pke.git
RUN python -m spacy download en_core_web_sm

CMD [ "python", "./download_models.py"]
