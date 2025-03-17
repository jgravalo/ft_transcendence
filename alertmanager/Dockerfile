# Use Alpine to ensure `wget` and SSL work correctly
FROM prom/alertmanager

COPY ./conf/alertmanager.yml /etc/alertmanager/alertmanager.yml

ENTRYPOINT [ "/bin/alertmanager", "--config.file=/etc/alertmanager/alertmanager.yml" ]