# Dockerfile para PostgreSQL
FROM postgres:13
COPY init.sql /docker-entrypoint-initdb.d/
COPY data.txt /docker-entrypoint-initdb.d/
