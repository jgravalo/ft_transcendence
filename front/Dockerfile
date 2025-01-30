# Usa la imagen oficial de Nginx como base
FROM nginx:alpine

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/share/nginx/html

# Copia el archivo de configuración personalizado a la ubicación predeterminada de Nginx
COPY ./conf/nginx.conf /etc/nginx/conf.d/default.conf

# Expone el puerto 80 para el tráfico HTTP
#EXPOSE 80
#EXPOSE 443

# Comando por defecto para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
