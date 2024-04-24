import grpc
from concurrent import futures
import time
import psycopg2
from ss_pb2_grpc import ServiceServicer, add_ServiceServicer_to_server  
from ss_pb2 import req, ress 


def postgres():
    try:
        conn = psycopg2.connect(
            dbname="base", 
            user="user",  
            password="password", 
            host="postgres", # nombre contenedor
            port="5432"  
        )
        return conn
    except Exception as e:
        print("error en postgres:", e)
        return None

#grcp :c
class Server(ServiceServicer):
    def consulta(self, request, context):
        conn = postgres()
        if not conn:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("error conectar")
            return ress() 
        cursor = conn.cursor()
        try:
            cursor.execute(request.query)
            rows = cursor.fetchall()  #base
            data = "\n".join(str(row) for row in rows) 
            return ress(data=data)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ress()  
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) #obtenido de chatgpt
    add_ServiceServicer_to_server(Server(), server)
    server.add_insecure_port("[::]:50051")  
    server.start()
    try:
        while True:
            time.sleep(86400) 
    except KeyboardInterrupt:
        server.stop(0)  
