import boto3
from iso639 import languages

def sentiment_analysis(text):
    language_code = client.detect_dominant_language(Text=text, )['Languages'][0]['LanguageCode']
    analysis = client.detect_sentiment(Text=text, LanguageCode=language_code)
    sentiment = str.lower(analysis['Sentiment'])
    sentiment_scores = analysis['SentimentScore']
    sentiment_scores = {k: format(v, '.3f') for k, v in sentiment_scores.items()}
    language_name = languages.get(alpha2=language_code).name
    return "The " + language_name + " text is " + sentiment + " with the scores: " + str(sentiment_scores)

client = boto3.client('comprehend')

eng = "The French Revolution was a period of social and political upheaval in France and its colonies beginning in 1789 and ending in 1799."
span = "El Quijote es la obra más conocida de Miguel de Cervantes Saavedra. Publicada su primera parte con el título de El ingenioso hidalgo don Quijote de la Mancha a comienzos de 1605, es una de las obras más destacadas de la literatura española y la literatura universal, y una de las más traducidas. En 1615 aparecería la segunda parte del Quijote de Cervantes con el título de El ingenioso caballero don Quijote de la Mancha."
fren = "Moi je n'étais rien Et voilà qu'aujourd'hui Je suis le gardien Du sommeil de ses nuits Je l'aime à mourir Vous pouvez détruire Tout ce qu'il vous plaira Elle n'a qu'à ouvrir L'espace de ses bras Pour tout reconstruire Pour tout reconstruire Je l'aime à mourir"
itan = "L'amor che move il sole e l'altre stelle."

print(sentiment_analysis(eng))
print(sentiment_analysis(span))
print(sentiment_analysis(fren))
print(sentiment_analysis(itan))