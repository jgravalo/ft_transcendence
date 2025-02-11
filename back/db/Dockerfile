# Usamos la imagen oficial de PostgreSQL como base
FROM postgres:15.10-alpine3.20

# Variables de entorno para configurar la base de datos
ENV POSTGRES_DB=mydatabase
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword

# Directorio de trabajo
WORKDIR /docker-entrypoint-initdb.d/

# Copiar scripts SQL de inicialización (opcional)
COPY ./init.sql .

# El puerto por defecto de PostgreSQL es 5432
EXPOSE 5432

# Los volúmenes se definirán en el docker-compose
VOLUME ["/var/lib/postgresql/data"]
