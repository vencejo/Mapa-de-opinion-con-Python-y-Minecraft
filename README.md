# mapaOpinionEnMinecraft

## Idea

Este proyecto es la continuación lógica del [taller sobre Python que impartimos en Uleila](http://www.guadatech.com/taller-de-minecraft-con-python-en/)

El el vamos mas allá de los conceptos básicos del lenguaje y se intenta hacer algo mas avanzado, 
experimentando con la representación de datos de Twitter en Minecraft y con un poco de IA mediante redes Bayesianas.

Para ello se crea un campo de opinion Bayesiano dividido entre dos zonas , positiva y negativa, 
a donde van entrando los tweets publicados por distintos Periodicos de tirada nacional, representados por bloques. 

 Coordenadas del campo:

 ```
(0,0,0)                       (16,0,0)                        (32,0,0)     x	                tiempo
   +------------------------------+------------------------------+       +------->       	+-------> 
   |                              |                              |       |			|
   |                              |                              |     z |	     Periodicos	|
   |                              |                              |       |			|	
   |   Zona Positiva              |     Zona Negativa            |       |			|
   |                              |                              |       v			v
   |                              |                              |
   |                              |                              |
   +------------------------------+------------------------------+
(0,0,16)                     (16,0,16)                         (32,0,16)  
```

Si rompemos un bloque que representa a un tweet este cambiará de sentimiento y pasara de estar en la zona positiva a la negativa,
o viceversa, cada vez que se realiza esta acción el clasificador Bayesiano es entrenado.

## Desarrollo

El programa es un ensayo conceptual totalmente en fase de desarrollo y absolutamente sin garantia de funcinamiento correcto.
Se ha desarrollado de manera interactiva utilizando los notebooks de ipython que se adjuntan.

En futuras versiones del programa esta pensado para que vaya recibiendo los tweets en tiempo real, tal y como se experimenta en 
el notebook "Extractor de Tweets", pero en la version actual lo que hace es simular este comportamiento tomando los tweets de 
un archivo previamente generado y guardado "Periodicos_4horas.json".

## Funcionamiento

Para hacer funcionar el proyecto en su versión actual hay que tener un Minecraft corriendo en una RaspberryPi o en el ordenador
que este en la misma red que el ordenador que ejecuta el programa, y luego conectarse desde este ordenador a la IP de la RaspberryPi
y ejecutar  el notebook "Mapa de opionion de Twitter con Minecraft.ipynb" o bien el programa "campoOpinion.py".

Alternativamente tambien se puede , y se debería, experimentar con los distintos notebooks que componen el proyecto donde se 
experimenta con el scrapping en Twitter, los clasificadores bayesianos, los hilos en Python etc ...