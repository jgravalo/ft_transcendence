FROM python:3.9

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Copia los archivos requeridos para la instalación
#COPY requirements.txt .

# Instala las dependencias de Python
#RUN pip install --no-cache-dir -r requirements.txt

RUN pip install django \
    django-cors-headers \
    django djangorestframework

#RUN pip install daphne

EXPOSE 8000

COPY ./app/ /

WORKDIR /app/

CMD ["python", "main.py", "runserver"]