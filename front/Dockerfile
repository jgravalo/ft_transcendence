FROM nginx:alpine

COPY src/ /usr/share/nginx/html/

#RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf
#COPY nginx.conf /etc/nginx/conf.d/

#COPY ./certificates/crazy-pong.com_private_key.key /etc/nginx/certs/
#COPY ./certificates/crazy-pong.com_ssl_certificate.cer /etc/nginx/certs/

EXPOSE 80
#EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]