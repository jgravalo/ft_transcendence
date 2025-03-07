# Usa la imagen oficial de Nginx como base
FROM nginx:alpine

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/share/nginx/html

# Copia el archivo de configuración personalizado a la ubicación predeterminada de Nginx
COPY ./conf/nginx.conf /etc/nginx/conf.d/default.conf

# Comando por defecto para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
