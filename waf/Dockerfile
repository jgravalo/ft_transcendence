# Usa la imagen oficial de Nginx como base
FROM owasp/modsecurity-crs:4.10.0-nginx-202501270601

# Copia el fichero de configuration para el "block" principal
#COPY ./conf/default.conf /etc/nginx/conf.d/default.conf

#Copia los cerificatos para el ssl
#COPY ./certs/nginx.crt /etc/nginx/certs/
#COPY ./certs/nginx.key /etc/nginx/certs/

# Expone el puerto 80/443 para el tráfico HTTP/HTTPS
EXPOSE 80
EXPOSE 443

# Comando por defecto para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]