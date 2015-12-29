
import mcpi.minecraft as minecraft
import conexionMinecraft as Conexion
import bloqueConTweet as Bloque
import math
import datetime
import time

class CampoOpinion:
    def __init__(self, conexion ,origenX, origenY, origenZ, largo, ancho, fechaInicio, fechaFinal, unidadesTiempo ):
        self.conexion = conexion
        self.origenX = origenX
        self.origenY = origenY
        self.origenZ = origenZ
        self.largo = largo
        self.ancho = ancho
        self.fechaInicio = fechaInicio
        self.fechaFinal = fechaFinal
        self.unidadesTiempo = unidadesTiempo
        self.tiempoParpadeo = 2 #segundos
        self.bloques = []
        
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
        
    def situarBloque(self, fechaBloque, creador,infoBloque,color, tipoBloque = 'positivo'):
        """ Da la coordenada x para situar el bloque en el campo de opinion segun la fecha de creacion del mismo
        Todos los bloques creados en el primer instante se situan en las coordenadas con origenX si tienen calificacion
        positiva y en origenX+largo si tienen clasificacion negativa, los que se crean
        un tiempo mas tarde se van situando en x que se van acercando al centro del campo
        La coordenada Z esta marcada por el creador del bloque, cada creador tiene una z asignada
        Los bloques del mismo creador , del mismo tipo y asignados a la misma x se apilan en el eje Y """
        
        if fechaBloque <= self.fechaInicio:
            return self.origenX
        if fechaBloque >= self.fechaFinal:
            return self.largo/2
        
        diferenciaInicialFinal = self.fechaFinal - self.fechaInicio
        diferenciaInicialBloque = fechaBloque - self.fechaInicio
        
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
        z = creador
        y = 1
        
        if tipoBloque != 'positivo':
            x , y, z = self.largo - x, y , z
         
        for bloque in self.bloques:
            if bloque.x == x and bloque.z == z:
                if bloque.y >= y:
                    y = bloque.y + 1
                    
        b = Bloque.Bloque(self.conexion, x, y, z,infoBloque,fechaBloque,color=color)
        b.ponerBloque()
        self.bloques.append(b)
        
    def vigilaCampo(self):
        while True:
            for bloque in self.bloques:
                
                # Los bloques recien puestos parpadean
                tiempoParpadeo = datetime.timedelta(seconds=self.tiempoParpadeo )
                ahora = datetime.datetime.now()
                #ahora = datetime.datetime(2003, 8, 4, 12, 56, 50)
                finParpadeo = bloque.fechaCreacion + tiempoParpadeo
                
                if ahora < finParpadeo:
                    if bloque.estado == 'parpadeo' and bloque.visible:
                        bloque.visible = False
                        conexion.mc.setBlock(bloque.x, bloque.y,bloque.z,0)
                    elif bloque.estado == 'parpadeo' and not bloque.visible:
                        bloque.visible = True
                        conexion.mc.setBlock(bloque.x, bloque.y,bloque.z,35,bloque.color)
                elif bloque.estado == 'parpadeo':
                    bloque.estado = 'sinParpadeo'
                    bloque.visible = True
                    conexion.mc.setBlock(bloque.x, bloque.y,bloque.z,35,bloque.color)
                
                # Sacando la info del bloque
                if bloque.haSidoGolpeado():
                    self.conexion.mc.postToChat(bloque.info)
                # Al destruir el bloque pasa de ser negativo a positivo y viceversa
                if conexion.mc.getBlock(bloque.x, bloque.y,bloque.z) == 0 and bloque.estado == 'sinParpadeo' :
                    if bloque.x < 16:
                        bloque.x = 16 + abs(16-bloque.x)
                    elif bloque.x > 16:
                        bloque.x = 16 - abs(16-bloque.x)
   
                    conexion.mc.setBlock(bloque.x, bloque.y,bloque.z,35,bloque.color)
    
        
        
            

""" Coordenadas del campo:

(0,0,0)                       (16,0,0)                        (32,0,0)              x
   +------------------------------+------------------------------+              +-------> 
   |                              |                              |              |
   |                              |                              |            z |
   |                              |                              |              |
   |                              |                              |              |
   |                              |                              |              v
   |                              |                              |
   |                              |                              |
   +------------------------------+------------------------------+
(0,0,16)                     (16,0,16)                         (32,0,16)  
   
"""

    
if __name__ == "__main__":
    conexion = Conexion.Conexion("192.168.1.38")

    intervaloTiempoCampo = datetime.timedelta(minutes = 16)
    fechaInicio = datetime.datetime.now()
    fechaFinal = fechaInicio  + intervaloTiempoCampo

    #(self, conexion ,origenX, origenY, origenZ, largo, ancho, fechaInicio, fechaFinal, unidades )
    campo = CampoOpinion(conexion, 0,0,0,32,16,fechaInicio,fechaFinal,'minutos')
    campo.dibujarCampo()
    #situarBloque(self, fechaBloque, creador,infoBloque,color, tipoBloque = 'positivo')
    fechaBloque1 = datetime.datetime.now()
    campo.situarBloque(fechaBloque1, 8, "1","rojo", 'negativo')
    time.sleep(5)
    fechaBloque2 = datetime.datetime.now()
    campo.situarBloque(fechaBloque2, 8, "2","azul", 'negativo')
    time.sleep(5)
    fechaBloque3 = datetime.datetime.now() 
    campo.situarBloque(fechaBloque3, 8, "3","verde", 'negativo')
    time.sleep(5)
    fechaBloque4 = datetime.datetime.now()
    campo.situarBloque(fechaBloque4, 8, "4","rojo", 'negativo')
    
    campo.vigilaCampo()
    