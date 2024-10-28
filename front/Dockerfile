FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ./src/ /usr/share/nginx/html/

COPY ./certs/nginx.crt /etc/nginx/certs/
COPY ./certs/nginx.key /etc/nginx/certs/

#EXPOSE 443
EXPOSE 80

COPY ./nginx.conf /etc/nginx/sites-enabled/default

CMD ["nginx", "-g", "daemon off;"]