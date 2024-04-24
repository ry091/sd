CREATE TABLE IF NOT EXISTS vehiculos (
    ID SERIAL PRIMARY KEY,
    Marca VARCHAR(10),
    Color VARCHAR(10),
    Modelo VARCHAR(20)
);

COPY vehiculos(ID, Marca, Color, Modelo) 
FROM '/docker-entrypoint-initdb.d/data.txt' 
WITH (FORMAT csv, HEADER false, DELIMITER ',');

