# Usar una imagen oficial de Python como base
FROM python:3.9-slim

# Instala las dependencias del sistema necesarias para compilar psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
	gcc \
    netcat-openbsd \
    curl \
    bash \
    gettext \
    jq \
    curl \
    && rm -rf /var/lib/apt/lists/* \
	&& apt-get clean

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requisitos (requirements.txt) al contenedor
COPY requirements.txt /app/

# Actualizar pip e instalar las dependencias de Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copiar el contenido del proyecto al contenedor
COPY ./app/ /app/

# Exponer el puerto en el que Django se ejecuta por defecto (8000)
EXPOSE 8000
# Expone el puerto en el que Daphne estará escuchando (por ejemplo, 8001)
EXPOSE 8001

# Definir las variables de entorno necesarias (por ejemplo, si usas PostgreSQL)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV CREATE_SUPERUSER=true
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_PASSWORD=admin
ENV DJANGO_SUPERUSER_EMAIL=admin@example.com

# Establece la variable de entorno para las configuraciones de Django
ENV DJANGO_SETTINGS_MODULE=app.settings
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Crear los archivos de migraciones, aplicar las migraciones y ejecutar el servidor de desarrollo
#CMD ["python", "manage.py", "migrate"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Comando para ejecutar Daphne en el contenedor
#CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "app.asgi:application"]

# Cambiar el shell por defecto a bash
SHELL ["/bin/bash", "-c"]

COPY init.sh .
RUN chmod +x init.sh
CMD ["/bin/bash", "./init.sh"]
