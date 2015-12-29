
import mcpi.minecraft as minecraft


class Conexion:
    
    def __init__(self, *args):
        self.mc = minecraft.Minecraft.create(*args)