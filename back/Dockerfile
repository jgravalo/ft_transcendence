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

# Cambiar el shell por defecto a bash
SHELL ["/bin/bash", "-c"]

COPY init.sh .
RUN chmod +x init.sh
CMD ["/bin/bash", "./init.sh"]
