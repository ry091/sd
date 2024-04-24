
FROM python:3.10

COPY cosas.txt /app/
COPY ss.proto /app/  
WORKDIR /app
RUN pip install -r cosas.txt  # Instalar las dependencias del archivo de requerimientos

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ss.proto
COPY . /app/


CMD ["tail", "-f", "/dev/null"]

