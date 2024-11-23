# Usar una imagen oficial de Python como base
FROM python:3.11-slim

# Instala las dependencias del sistema necesarias para compilar psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && apt-get clean

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requisitos (requirements.txt) al contenedor
COPY requirements.txt /app/

# Instalar las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install django django-cors-headers djangorestframework channels
#RUN pip install daphne

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

# Crear los archivos de migraciones, aplicar las migraciones y ejecutar el servidor de desarrollo
#CMD ["python", "manage.py", "migrate"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Comando para ejecutar Daphne en el contenedor
#CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "app.asgi:application"]
COPY init.sh .
RUN chmod +x init.sh
CMD ["sh", "init.sh"]
