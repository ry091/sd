# Imagen base de Python
FROM python:3.10

# Instalar dependencias
COPY cosas.txt /app/
WORKDIR /app
RUN pip install -r cosas.txt

# Copiar el archivo proto y compilar
COPY ss.proto /app/  
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ss.proto

# Copiar el código del servidor después de compilar el proto
COPY . /app/

# Definir el comando para iniciar el servidor
CMD ["python", "server.py"]

