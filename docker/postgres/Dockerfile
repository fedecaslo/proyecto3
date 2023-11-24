FROM postgres:12

COPY rome_u_journeys.csv /docker-entrypoint-initdb.d/rome_u_journeys.csv

ENV POSTGRES_USER admin
ENV POSTGRES_PASSWORD admin
ENV POSTGRES_DB rome

CMD ["postgres"]