
import mcpi.minecraft as minecraft
import conexionMinecraft as Conexion
import conexionLocalhost as ConexionLocal
import bloqueConTweet as Bloque
import math
import datetime
import time
import json
import threading
import preprocesadorTweets as preprocesador
import clasificadorPrensa 
import logging


class CampoOpinion(threading.Thread):

    def __init__(self, conexion ,origenX, origenY, origenZ, largo, ancho, fechaInicio, fechaFinal, unidadesTiempo ):
        threading.Thread.__init__(self)
        self.colores = { 'elmundoes':("blanco","naranja"), 'el_pais':("purpura","azul"), 'abc_es':("amarillo","verde"),
                           'larazon_es':("rosa","cacao"), 'eldiarioes':("gris","turquesa"),'lavanguardia':("lila","azul_oscuro"),
                           'publico_es':("marron","verde oscuro"),'20m':("rojo","negro") }
        self.conexion = conexion
        self.origenX = origenX
        self.origenY = origenY
        self.origenZ = origenZ
        self.largo = largo
        self.ancho = ancho
        self.fechaInicio = fechaInicio
        self.fechaFinal = fechaFinal
        self.unidadesTiempo = unidadesTiempo
        self.tiempoParpadeo = 4 #segundos
        self.bloques = {}
        
    def dibujarCampo(self):
        # Aclaramos el terreno
        self.conexion.mc.setBlocks(self.origenX-self.largo*2, self.origenY , self.origenZ-self.largo*2,\
                          self.origenX +self.largo*2, self.origenY + self.largo*2, self.origenY + self.largo*2, 0)

        # Ponemos el suelo
        self.conexion.mc.setBlocks(self.origenX, self.origenY-2 ,self.origenZ ,\
                          self.origenX+self.largo, self.origenY, self.origenZ+self.largo/2, 35,0)
        self.conexion.mc.setBlocks(self.origenX + 17, self.origenY ,self.origenZ, \
                          self.origenX +self.largo, self.origenY, self.origenZ+self.largo/2, 35,7)
        # Bordes del campo+
        self.conexion.mc.setBlocks(self.origenX-1, self.origenY , self.origenZ-1, self.origenX, self.origenY-1, self.origenZ+16, 35,15)
        self.conexion.mc.setBlocks(self.origenX-1, self.origenY , self.origenZ-1, self.origenX+32, self.origenY, self.origenZ-1, 35,15)
        self.conexion.mc.setBlocks( self.origenX, self.origenY-1 , self.origenZ+16, self.origenX+32, self.origenY, self.origenZ+16, 35,15)
        self.conexion.mc.setBlocks( self.origenX + 32, self.origenY , self.origenZ-1, self.origenX+32, self.origenY, self.origenZ+16, 35,15)
        self.conexion.mc.setBlocks( self.origenX + 16, self.origenY , self.origenZ-1, self.origenX+16, self.origenY, self.origenZ+16, 35,15)

        # Teletrasportamos a Steve
        self.conexion.mc.player.setTilePos(self.origenX+16, self.origenY+1, self.origenZ+16)
        
    def situarBloque(self, fechaCreacionTweet,periodico,infoBloque,tweet,color, sentimiento = 'positive'):
        """ Da la coordenada x para situar el bloque en el campo de opinion segun la fecha de creacion del mismo
        Todos los bloques creados en el primer instante se situan en las coordenadas con origenX si tienen calificacion
        positiva y en origenX+largo si tienen clasificacion negativa, los que se crean
        un tiempo mas tarde se van situando en x que se van acercando al centro del campo
        La coordenada Z esta marcada por el creador del bloque, cada creador tiene una z asignada
        Los bloques del mismo creador , del mismo tipo y asignados a la misma x se apilan en el eje Y """
        
        if fechaCreacionTweet <= self.fechaInicio:
            return self.origenX
        if fechaCreacionTweet >= self.fechaFinal:
            return self.largo/2
        
        diferenciaInicialFinal = self.fechaFinal - self.fechaInicio
        diferenciaInicialBloque = fechaCreacionTweet - self.fechaInicio
        
        if self.unidadesTiempo == 'minutos':
            instanteDiferenciaInicialFinal = (diferenciaInicialFinal.seconds//60)%60
            instanteDiferenciaInicialBloque = (diferenciaInicialBloque.seconds//60)%60
        elif self.unidadesTiempo == 'horas':
            instanteDiferenciaInicialFinal = diferenciaInicialFinal.seconds//3600
            instanteDiferenciaInicialBloque = diferenciaInicialBloque.seconds//3600
        elif self.unidadesTiempo == 'dias':
            instanteDiferenciaInicialFinal = diferenciaInicialFinal.days
            instanteDiferenciaInicialBloque = diferenciaInicialBloque.days
            
        x = (instanteDiferenciaInicialBloque * self.largo/2)/instanteDiferenciaInicialFinal
        z = coordenadasZ[periodico]
        y = self.origenY + 2
        
        if sentimiento != 'positive':
            x , y, z = self.largo - x, y , z
         
        for pos in self.bloques:
            if pos[0] == x and pos[2] == z:
                if pos[1] >= y:
                    y = pos[1] + 1
        
        fechaCreacionBloque = datetime.datetime.now()
        b = Bloque.Bloque(self.conexion, x, y, z,infoBloque,tweet, fechaCreacionTweet,fechaCreacionBloque,periodico, \
                          color=color, sentimiento=sentimiento)
        b.ponerBloque()
        self.bloques[(b.x, b.y, b.z)] = b
        
        
        

""" Coordenadas del campo:

(0,0,0)                       (16,0,0)                        (32,0,0)              x
   +------------------------------+------------------------------+              +-------> 
   |                              |                              |              |
   |                              |                              |            z |
   |                              |                              |              |
   |   Zona Positiva              |     Zona Negativa            |              |
   |                              |                              |              v
   |                              |                              |
   |                              |                              |
   +------------------------------+------------------------------+
(0,0,16)                     (16,0,16)                         (32,0,16)  
   
"""
                

class SimulaLlegadaTweets(threading.Thread):
    """ Simula la llegada de tweets """
    def __init__(self, campo,clasificador, periodicos, tweets, maxTweets,segundosEntreTweets,llaveConexion,
                 llaveClasificador):
        threading.Thread.__init__(self)
        self.campo = campo
        self.clasificador = clasificador
        self.periodicos = periodicos
        self.tweets = tweets
        self.maxTweets = maxTweets
        self.segundosEntreTweets = segundosEntreTweets
        self.llaveConexion = llaveConexion
        self.llaveClasificador = llaveClasificador
        
    def run(self):
        cont = 0
        periodicosCompletados = 0
        numTweets = 0
        while periodicosCompletados < len(self.periodicos) and numTweets < self.maxTweets:
            for periodico in self.periodicos:
                if periodico in self.tweets.keys():
                    if  cont < len(self.tweets[periodico]):
                        fecha = datetime.datetime.strptime(self.tweets[periodico][cont][0], "%Y-%m-%d %H:%M:%S")
                        color = self.campo.colores[periodico][0] if cont%2 else self.campo.colores[periodico][1] 
                        tweet = preprocesador.eliminaTildes(self.tweets[periodico][cont][1]).encode('ascii','ignore')
                        if self.clasificador is not None:
                            self.llaveClasificador.acquire()
                            sentimiento = self.clasificador.clasificaNuevoTweet(tweet)
                            self.llaveClasificador.release()
                        else:
                            sentimiento = 'positive'
                        informacion = periodico +" "+ self.tweets[periodico][cont][0] + " "*4 + \
                                     tweet + " "*200
                        self.llaveConexion.acquire()
                        self.campo.situarBloque(fecha, periodico,informacion,tweet,color=color,sentimiento=sentimiento)
                        self.llaveConexion.release()
                        time.sleep(segundosEntreTweets)
                        numTweets += 1
                        if numTweets >= self.maxTweets:
                            break
                    else:
                        periodicosCompletados += 1
            cont += 1
        if log:
            logging.info( "Fin llegada de tweets" )
            for pos, bloque in self.campo.bloques.items():
                logging.info("Llave: %s", pos)
                logging.info("Valor: %s", bloque)
            logging.info("Num Bloques: %d", len(self.campo.bloques))
          
                
                
class ParpadeoRecienLlegados(threading.Thread):
    """ Los bloques recien puestos parpadean """
    def __init__(self, conexion, campo,llaveConexion,llaveClasificador):
        threading.Thread.__init__(self)
        self.tiempoParpadeo = datetime.timedelta(seconds=5 )
        self.conexion = conexion
        self.campo = campo
        self.llaveConexion = llaveConexion
        self.llaveClasificador = llaveClasificador
    

    def run(self):
       
        while True:
            time.sleep(1)
            for pos, bloque in self.campo.bloques.items():
                ahora = datetime.datetime.now()
                finParpadeo = bloque.fechaCreacionBloque + self.tiempoParpadeo

                if ahora < finParpadeo:
                    self.llaveConexion.acquire()
                    if bloque.estado == 'parpadeo' and bloque.visible:
                        bloque.visible = False
                        color = bloque.dameCodigoColor(self.campo.colores[bloque.periodico][ (bloque.y+1)%2 ])
                        self.conexion.mc.setBlock(bloque.x, bloque.y,bloque.z,35,color)
                    elif bloque.estado == 'parpadeo' and not bloque.visible:
                        bloque.visible = True
                        color = bloque.dameCodigoColor(self.campo.colores[bloque.periodico][bloque.y%2])
                        self.conexion.mc.setBlock(bloque.x, bloque.y,bloque.z,35,color)
                    self.llaveConexion.release()

                else:
                    bloque.estado = 'sinParpadeo'
                    bloque.visible = True
        
        
class VigilaCampo():
    def __init__(self,conexion,campo,clasificador,llaveConexion,llaveClasificador ):
        
        self.conexion = conexion
        self.campo = campo
        self.clasificador = clasificador
        self.llaveConexion = llaveConexion
        self.llaveClasificador = llaveClasificador
    
    
    def run(self):
        
        distanciaMinParaDeteccion = 2
        distanciaBloqueMasCercano =  1000
        bloqueMasCercanoAJugador = None
        ultimaPosicionConocida = None
        mensajeMostrado = False
        perdidaConexion = False
          
        while True: #Ciclo continuo de ejecucion de la funcion
            while True: #Ciclo continuo de intentos de conexion
                try:
                    self.llaveConexion.acquire()
                    posicionJugador = self.conexion.mc.player.getTilePos()
                    #if log:
                       # logging.info("Conexion exitosa, coords Jugador : %s", str((posicionJugador.x,
                                                                                  # posicionJugador.y,
                                                                                  # posicionJugador.z)))
                    self.llaveConexion.release()
                    
                    (x,y,z) = (posicionJugador.x, posicionJugador.y , posicionJugador.z)  
                    inc = (-3,-2,-1,0,1,2,3)  #Inc menos amplio inc = (-1,0,1)
                    posicionesAdyacentes = [(x+i, y+j, z+k) for i in inc for j in inc for k in inc
                            if (i,j,k) != (0,0,0)]
                    bloquesAdyacentes = [self.campo.bloques[pos] for pos in posicionesAdyacentes 
                                            if self.campo.bloques.has_key(pos)]

                    for bloque in bloquesAdyacentes:
                        # Al destruir el bloque pasa de ser negativo a positivo y viceversa
                        self.llaveConexion.acquire()
                        tipoBloque = self.conexion.mc.getBlock(bloque.x, bloque.y,bloque.z)
                        self.llaveConexion.release()

                        if tipoBloque == 0: #and bloque.estado == 'sinParpadeo' :

                            bloque.estado = "parpadeo"
                            if bloque.x < 16:
                                del self.campo.bloques[(bloque.x,bloque.y, bloque.z)]
                                bloque.x = 16 + abs(16-bloque.x)
                                bloque.sentimiento = "negative"
                                self.llaveClasificador.acquire()
                                self.clasificador.cambiaSentimiento(bloque.tweet, "negative")
                                self.llaveClasificador.release()
                            elif bloque.x > 16:
                                del self.campo.bloques[(bloque.x,bloque.y, bloque.z)]
                                bloque.x = 16 - abs(16-bloque.x)
                                bloque.sentimiento = "positive"
                                self.llaveClasificador.acquire()
                                self.clasificador.cambiaSentimiento(bloque.tweet, "positive")
                                self.llaveClasificador.release()
                            #clasificador.clasificadorEntrenado.show_most_informative_features(10)
                            self.llaveConexion.acquire()
                            hayBloqueEnDestino = True
                            while hayBloqueEnDestino:
                                tipoBloque = self.conexion.mc.getBlock(bloque.x, bloque.y,bloque.z)
                                if tipoBloque != 0:
                                    bloque.y += 1
                                else:
                                    hayBloqueEnDestino = False
                            self.conexion.mc.setBlock(bloque.x, bloque.y,bloque.z,35,bloque.color)
                            self.llaveConexion.release()
                            self.campo.bloques[(bloque.x,bloque.y, bloque.z)] = bloque
                            if log:
                                logging.info("")
                                logging.info("Tweet cambiado de sentimiento")
                                logging.info("Nuevas coordenadas: %s", str((bloque.x,bloque.y,bloque.z)))

                        # Sacando la info del bloque
                        distanciaBloqueAJugador = bloque.distancia(posicionJugador)
                        if  distanciaBloqueAJugador < distanciaMinParaDeteccion and distanciaBloqueAJugador < distanciaBloqueMasCercano :
                            distanciaBloqueMasCercano = distanciaBloqueAJugador
                            bloqueMasCercanoAJugador = bloque


                    if bloqueMasCercanoAJugador != None and not mensajeMostrado:
                        bloqueMasCercanoAJugador.muestraInfo()
                        distanciaBloqueMasCercano =  1000
                        bloqueMasCercanoAJugador = None
                        mensajeMostrado = True
                        tiempoSiguienteMensaje = datetime.datetime.now() + datetime.timedelta(seconds=2 )
                    elif bloqueMasCercanoAJugador != None and datetime.datetime.now() > tiempoSiguienteMensaje:
                        mensajeMostrado = False

                except :
                    if log:
                        logging.info("Error conexion , reintentando...")
                    self.llaveConexion.release()
                    continue
                break
                    
       
    
if __name__ == "__main__":
    
    import logging
    reload(logging)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(asctime)s %(message)s',filename='eventos.log',filemode='w',level=logging.DEBUG)
    
    conexion = ConexionLocal.Conexion() 
    #conexion = Conexion.Conexion("192.168.1.38")
    
    # Llaves para tener acceso a los recursos mutuamente excluyentes
    llaveClasificador = threading.Lock()
    llaveConexion = threading.Lock()
    
    periodicos = ['elmundoes', 'el_pais', 'abc_es','larazon_es',
                  'eldiarioes','publico_es','20m']
    
    coordenadasZ = { 'elmundoes':2, 'el_pais':4, 'abc_es':6,'larazon_es':8,
                  'eldiarioes':10,'publico_es':12,'20m':14 }
    
    tweets = preprocesador.leeArchivoTweets("periodicos_4horas.json")
    
    fechaInicio = datetime.datetime.strptime(tweets["inicio"], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(minutes = 30)
    intervaloTiempoCampo = datetime.timedelta(hours = 5)
    fechaFinal = fechaInicio  + intervaloTiempoCampo
    coordXInicio = 0
    coordYInicio = 100
    coordZInicio = 0
    campo = CampoOpinion(conexion, coordXInicio,coordYInicio,coordZInicio,32,16,fechaInicio,fechaFinal,'horas')
    campo.dibujarCampo()
    
    """ Coordenadas del campo:

    (0,0,0)                       (16,0,0)                        (32,0,0)              x
       +------------------------------+------------------------------+              +-------> 
       |                              |                              |              |
       |                              |                              |            z |
       |                              |                              |              |
       |   Zona Positiva              |     Zona Negativa            |              |
       |                              |                              |              v
       |                              |                              |
       |                              |                              |
       +------------------------------+------------------------------+
    (0,0,16)                     (16,0,16)                         (32,0,16)  

    """
    
    faseDeLaPresentacion = "intro"     #valores posibles "intro", "bayes"
    log = True
    
    if faseDeLaPresentacion == "intro": 
        numTweetsParaProcesar = 195
        segundosEntreTweets = 0
        clasificador = None
    elif faseDeLaPresentacion == "bayes":
        numTweetsParaProcesar = 195
        segundosEntreTweets = 3
        clasificador = clasificadorPrensa.ClasificadorPrensa()
    
    #if faseDeLaPresentacion == "bayes":
     #   parpadeo = ParpadeoRecienLlegados(conexion, campo,llaveConexion,llaveClasificador)
      #  parpadeo.start()
    
    tweetsLlegando = SimulaLlegadaTweets(campo, clasificador, periodicos, tweets,numTweetsParaProcesar,segundosEntreTweets,llaveConexion,llaveClasificador)
    tweetsLlegando.start()
    
    vigilaCampo = VigilaCampo(conexion,campo,clasificador,llaveConexion,llaveClasificador )
    vigilaCampo.run()
    
    