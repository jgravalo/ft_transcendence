FROM python:3.8

RUN apt install python3 python3-pip

RUN pip install django

RUN pip install django-cors-headers

#RUN pip install daphne

COPY ./app/ /

WORKDIR /app/

CMD ["python", "main.py"]