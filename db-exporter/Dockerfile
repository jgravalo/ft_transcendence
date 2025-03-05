FROM prometheuscommunity/postgres-exporter

COPY ./conf/entrypoint.sh /app/entrypoint.sh

ENTRYPOINT [ "/bin/bash", "/app/entrypoint.sh"]
