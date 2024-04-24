import grpc
import redis
import hashlib
from ss_pb2_grpc import ServiceStub# stub (cliente) servicer (servidor)
from ss_pb2 import req  # request
import time  
import plotext as plt
from rediscluster import RedisCluster

class Cachety:
    def __init__(self, politica):
        self.redis_conn = None  
        self.time_cache = []
        self.politica = politica 
        nodes = [
            {"host": "cache-p1", "port": 6380},
            {"host": "cache-p2", "port": 6381},
            {"host": "cache-p3", "port": 6382},
        ]

        # Crea una instancia de RedisCluster
        try:
            self.redis_conn = RedisCluster(startup_nodes=nodes, decode_responses=True)
            print("Clúster Redis conectado correctamente")
            self.conf_polit()
        except Exception as e:
            print(f"Error al inicializar la conexión Redis Cluster: {e}")
    def get_slot(self, key):
        hash_value = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        return hash_value % len(self.redis_instances)  # Devuelve un índice entre 0 y 2

    def obt_cache(self, key):
        slot = self.get_slot(key)
        value = self.redis_instances[slot].get(key)

        if value is None:
            print(f"La clave '{key}' no se encontró en la caché.")
        
        return value
    
    def cass_cache(self, key, value):
        slot = self.get_slot(key)
        self.redis_instances[slot].set(key, value)

    def conf_polit(self):#chatgpt
        for instance in self.redis_instances:
            if self.politica == "LRU":
                instance.config_set("maxmemory-policy", "allkeys-lru")
            elif self.politica == "MRU":
                instance.config_set("maxmemory-policy", "allkeys-mru")

    def borrar_cache(self):
        for instance in self.redis_instances:
            instance.flushall()

    def register_time(self, tiempo):
        if isinstance(tiempo, (int, float)):
            self.time_cache.append(tiempo)

    def verificar_conexion(redis_instances):
        for i, instance in enumerate(redis_instances):
            try:
                instance.ping()
                print(f"Nodo {i} está conectado correctamente.")
            except redis.ConnectionError:
                print(f"Error al conectar al nodo {i}.")
            

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
    cache.redis_instances()
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
