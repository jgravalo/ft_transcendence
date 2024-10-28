# Usar una imagen oficial de Python como base
FROM python:3.11-slim

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

# Definir las variables de entorno necesarias (por ejemplo, si usas PostgreSQL)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear los archivos de migraciones, aplicar las migraciones y ejecutar el servidor de desarrollo
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
