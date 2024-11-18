# Usa la imagen oficial de Nginx como base
FROM nginx:alpine

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/share/nginx/html

#RUN rm /etc/nginx/conf.d/default.conf

# Copia el archivo de configuración personalizado a la ubicación predeterminada de Nginx
#COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./nginx.conf /etc/nginx/sites-enabled/default
#COPY nginx.conf /etc/nginx/conf.d/
#RUN rm /etc/nginx/conf.d/default.conf
COPY ./certs/nginx.crt /etc/nginx/certs/
COPY ./certs/nginx.key /etc/nginx/certs/


# Copia los archivos estáticos de la aplicación al directorio HTML de Nginx
#COPY ./html /usr/share/nginx/html
COPY src/ /usr/share/nginx/html/.

# Expone el puerto 80 para el tráfico HTTP
EXPOSE 80
EXPOSE 443

# Comando por defecto para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
