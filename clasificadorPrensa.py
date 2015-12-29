
import preprocesadorTweets as preprocesador
import clasificadorBayesiano
import nltk

class ClasificadorPrensa():
    def __init__(self):
        self.periodicos = ['elmundoes', 'el_pais', 'abc_es','larazon_es',
                              'eldiarioes','publico_es','20m']

        self.periodicosEntrenamiento = ['elmundoes', 'el_pais', 'abc_es','eldiarioes','20m']
        self.tweetsBaseProcesados = self.extraeTweets("periodicos_4horas.json", self.periodicos)
        self.tweetsEntrenamientoProcesados  = self.extraeTweets("periodicos.json", self.periodicosEntrenamiento)
        self.clasificador = clasificadorBayesiano.Clasificador(self.tweetsBaseProcesados)  
        self.clasificadorEntrenado = self.clasificador.entrenaClasificador(self.tweetsEntrenamientoProcesados)
        
    def extraeTweets(self, archivo, periodicos):     
        tweets = preprocesador.leeArchivoTweets(archivo)
        tweetsProcesados = []
        for periodico in periodicos:
            tweetsProcesados.extend(preprocesador.preprocesaTweets(tweets,periodico))
        return tweetsProcesados
    
    def clasificaNuevoTweet(self, nuevoTweet_texto):
        """ Da la clasificacion del Tweet segun el clasificador bayesiano ('positive' o 'negative') 
        y vuelve a entrenar al clasificador con esta informacion"""
        nuevoTweet_sentimiento = self.clasificador.clasifica(self.clasificadorEntrenado, nuevoTweet_texto)
        nuevoTweetProcesado = preprocesador.preprocesaTweet(nuevoTweet_texto, nuevoTweet_sentimiento)
        #Vuelvo a entrenar al clasificador con el nuevo tweet que ha entrado junto con todos los anteriores
        self.tweetsEntrenamientoProcesados.append(nuevoTweetProcesado)
        self.clasificadorEntrenado = self.clasificador.entrenaClasificador(self.tweetsEntrenamientoProcesados)
        return nuevoTweet_sentimiento
        
    def cambiaSentimiento(self, tweet_texto,nuevoSentimiento):
        self.tweetsEntrenamientoProcesados = self.clasificador.cambiaSentimiento(self.tweetsEntrenamientoProcesados, 
                                                                                    tweet_texto, nuevoSentimiento)

        self.clasificadorEntrenado = self.clasificador.entrenaClasificador(self.tweetsEntrenamientoProcesados)
    