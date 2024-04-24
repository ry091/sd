import grpc
import redis
from ss_pb2_grpc import ServiceStub# stub (cliente) servicer (servidor)
from ss_pb2 import req  # request
import time  # Para medir el tiempo de respuesta
import plotext as plt
from redis.sentinel import Sentinel

class Cachety:  # implementado con ayuda de copilot
    def __init__(self,politica):
    
        self.redis_conn = None  
        self.time_cache = []
        self.politica = politica

        try:
            sentinel_hosts = [("cache-master", 6383)]  # Cambia a la configuración adecuada
            sentinel = Sentinel(sentinel_hosts, socket_timeout=0.1)
            self.redis_conn = sentinel.master_for("mymaster", decode_responses=True)

            print("Caché replicada conectada")
            self.conf_polit() 
        except Exception as e:
            print(f"Error al inicializar la conexión Redis: {e}")

    def obt_cache(self, key):
        if not self.redis_conn:
            print("Conexión con Redis no está configurada.")
            return None
        try:
            value = self.redis_conn.get(key)  # Obtener el valor desde el maestro
            return value
        except Exception as e:
            print(f"Error al obtener datos de la caché: {e}")
            return None

    def cass_cache(self, key, value):
        if not self.redis_conn:
            print("Conexión con Redis no está configurada.")
            return

        try:
            self.redis_conn.set(key, value)  # Guardar el valor en el maestro
        except Exception as e:
            print(f"Error al guardar datos en la caché: {e}")

    def conf_polit(self):# codigo ontenido por chatgpt y repositorios en github
        if self.politica == "LRU":
            self.redis_conn.config_set("maxmemory-policy", "allkeys-lru")
        elif self.politica == "MRU":
            self.redis_conn.config_set("maxmemory-policy", "allkeys-mru")

    def borrar_cache(self):
        self.redis_conn.flushall()
        print("cache borrada.")
            

    def register_time(self, tiempo):
        if isinstance(tiempo, (int, float)):
            self.time_cache.append(tiempo)
        

# grcp con servidor
grpc_com = grpc.insecure_channel("server:50051")
grpc_stub = ServiceStub(grpc_com) 

def consultaa(cache):
    sql = input("consulta sql: ")
    ini = time.time()
    resultado = cache.obt_cache(sql) 

    if resultado:
        fin = time.time()
        cache.register_time(fin-ini)
        print("( desde cache)", resultado)
    else:
        
        response = grpc_stub.consulta(req(query=sql)) #grcp ser
        cache.cass_cache(sql, response.data)  
        fin= time.time()
        cache.register_time(fin-ini)
        print("(desde servidor)", response.data)
        


def graficar(cache):
        consultas = list(range(1, len(cache.time_cache) + 1))
        plt.plot(consultas, cache.time_cache, label="Tiempo de respuesta")
        plt.xlabel("Consulta")
        plt.ylabel("Tiempo (s)")
        plt.title("Tiempos de respuesta por consulta")
        plt.show()
   



if __name__ == "__main__":
    politica= input("tipo de politica: 1)MRU, 2)LRU:   ")
    cache = Cachety(politica)
    while True:
        print(" opciones: 1) Realizar consulta, 2) Gráfica, 3) Salir:    ")
        opcion = input("n° de opcion: ")

        if opcion == "1":
            consultaa(cache) 
        elif opcion == "2":
            graficar(cache)
        elif opcion == "3":
            cache.borrar_cache()
            break  #salir
