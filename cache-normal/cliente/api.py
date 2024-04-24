import grpc
import redis
from ss_pb2_grpc import ServiceStub# stub (cliente) servicer (servidor)
from ss_pb2 import req  # request
import time  
import plotext as plt


class Cachety:  # implementado con ayuda de copilot
    def __init__(self,politica):
        self.redis_conn = None  
        self.time_cache = []
        self.politica = politica 
        self.redis_conn = redis.Redis(host="cache-normal", port=6379)
        self.conf_polit()

    def obt_cache(self, key):
         return self.redis_conn.get(key)

    def cass_cache(self, key, value):
        self.redis_conn.set(key, value)    

    def conf_polit(self):# codigo ontenido por chatgpt y repositorios en github
        if self.politica == "LRU":
            self.redis_conn.config_set("maxmemory-policy", "allkeys-lru")
        elif self.politica == "MRU":
            self.redis_conn.config_set("maxmemory-policy", "allkeys-mru")

    def borrar_cache(self):
        if self.redis_conn:
            try:
                self.redis_conn.flushall()
                print("cache borrada.")
            except Exception as e:
                print(f"error borrar la caché: {e}")

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
