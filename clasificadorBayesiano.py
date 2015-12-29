import preprocesadorTweets as preprocesador
import nltk
from nltk.corpus import stopwords


class Clasificador():
    
    def __init__(self, train_tweets):
        self.word_features = self.get_word_features(self.get_words_in_tweets(train_tweets))
        
    # The list of word features need to be extracted from the tweets. 
    # It is a list with every distinct words ordered by frequency of appearance.
    # We use the following function to get the list plus the two helper functions.

    def get_words_in_tweets(self,tweets):
        all_words = []
        for (words, sentiment) in tweets:
            all_words.extend(words)
        return all_words

    def get_word_features(self,wordlist):
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features


    # To create a classifier, we need to decide what features are relevant. 
    # To do that, we first need a feature extractor. 
    # The one we are going to use returns a dictionary indicating what words are contained in the input passed. 
    # Here, the input is the tweet. We use the word features list defined above along with the input 
    # to create the dictionary

    def extract_features(self,document):
        document_words = set(document)
        features = {}
        for word in self.word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features


    def entrenaClasificador(self,train_tweets):
        # With our feature extractor, we can apply the features to our classifier using the method apply_features. 
        # We pass the feature extractor along with the tweets list defined above.
        training_set = nltk.classify.apply_features(self.extract_features, train_tweets)
        # Now that we have our training set, we can train our classifier.
        return nltk.NaiveBayesClassifier.train(training_set)

    def clasifica(self,clasificador, tweet):
        return clasificador.classify(self.extract_features(tweet.split()))

    def cambiaSentimiento(self,tweets, tweetConNuevoSentimiento, sentimiento):
        """Cambiando un tweet de sentimiento
        tweetConNuevoSentimiento = 'RT @elpais_opinion: No se equivoquen, la campa\xf1a electoral es una 
                                    extirpaci\xf3n de los recuerdos. David Trueba explica por qu\xe9 https://t.co/u\u2026' """

        tweetConNuevoSentimiento = preprocesador.preprocesaTweet(tweetConNuevoSentimiento, sentimiento)
        for index,tweet in enumerate(tweets):
            if tweets[index][0] == tweetConNuevoSentimiento[0]:
                del tweets[index]
                tweets.append(tweetConNuevoSentimiento)
        return tweets


