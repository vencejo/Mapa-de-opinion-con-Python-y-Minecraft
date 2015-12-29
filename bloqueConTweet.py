
import mcpi.minecraft as minecraft
import math
import datetime

# Clase bloque

class Bloque:
    def __init__(self,conexion , x , y, z, info,tweet,fechaCreacionTweet,fechaCreacionBloque,periodico, tipo = 35, color = "blanco",\
                 estado="parpadeo",visible = True, sentimiento="positive" ):
        self.mc = conexion.mc
        self.x = x
        self.y = y
        self.z = z
        self.fechaCreacionTweet = fechaCreacionTweet
        self.fechaCreacionBloque = fechaCreacionBloque
        self.periodico = periodico
        self.info = info
        self.tweet = tweet
        self.tipo = tipo
        self.estado = estado
        self.visible = visible
        self.sentimiento = sentimiento
        self.color = self.dameCodigoColor(color)
      
    def __repr__(self):
        return "Bloque en %.1f %.1f %.1f con info %s"%( self.x, self.y, self.z, self.info)
        
    def dameCodigoColor(self, color):
        """ Esta funcion coge un color y te devuelve el codigo del bloque correspondiente de lana con ese color"""
    
        # Esto de abajo es un diccionario que se estructura en elementos de la forma llave:valor
        wool = {"blanco": 0, "naranja": 1, "purpura": 2, "azul": 3, "amarillo": 4, "verde": 5, "rosa": 6, "cacao": 7,
            "gris": 8, "turquesa": 9, "lila": 10, "azul oscuro": 11, "marron": 12, "verde oscuro": 13, 
            "rojo": 14,"negro": 15}
    
        return wool[color]
        
    def ponerBloque(self):
        self.mc.setBlock(self.x, self.y, self.z, self.tipo , self.color)
    
    def distancia(self, punto):
        xd = self.x - punto.x
        yd = self.y - punto.y
        zd = self.z - punto.z
        return math.sqrt((xd*xd) + (yd*yd) + (zd*zd))
    
    def muestraInfo(self):
        self.mc.postToChat(self.info)
        
    def haSidoGolpeado(self):
        hits = self.mc.events.pollBlockHits()
        for hit in hits:
            if hit.pos.x == self.x and hit.pos.y == self.y and hit.pos.z == self.z:
                return True
            
    def haSidoDestruido(self):
        if self.mc.getBlock(self.x, self.y, self.z) == 0: 
            return True
                

            