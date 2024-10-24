FROM nginx:alpine

COPY src/ /usr/share/nginx/html/

WORKDIR /usr/share/nginx/html/

EXPOSE 443

EXPOSE 8080

COPY ./nginx.conf /etc/nginx/sites-enabled/default

CMD ["nginx", "-g", "daemon off;"]