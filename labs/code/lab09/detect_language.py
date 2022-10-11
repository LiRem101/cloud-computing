import boto3
from iso639 import languages

def create_answer(response):
    language_name = languages.get(alpha2=response['Languages'][0]['LanguageCode']).name
    language_store = int(response['Languages'][0]['Score'] * 100)
    return language_name + " detected with " + str(language_store) + "% confidence"

client = boto3.client('comprehend')

eng = "The French Revolution was a period of social and political upheaval in France and its colonies beginning in 1789 and ending in 1799."
span = "El Quijote es la obra más conocida de Miguel de Cervantes Saavedra. Publicada su primera parte con el título de El ingenioso hidalgo don Quijote de la Mancha a comienzos de 1605, es una de las obras más destacadas de la literatura española y la literatura universal, y una de las más traducidas. En 1615 aparecería la segunda parte del Quijote de Cervantes con el título de El ingenioso caballero don Quijote de la Mancha."
fren = "Moi je n'étais rien Et voilà qu'aujourd'hui Je suis le gardien Du sommeil de ses nuits Je l'aime à mourir Vous pouvez détruire Tout ce qu'il vous plaira Elle n'a qu'à ouvrir L'espace de ses bras Pour tout reconstruire Pour tout reconstruire Je l'aime à mourir"
itan = "L'amor che move il sole e l'altre stelle."

response_eng = client.detect_dominant_language(Text=eng,)
response_span = client.detect_dominant_language(Text=span,)
response_fren = client.detect_dominant_language(Text=fren,)
response_itan = client.detect_dominant_language(Text=itan,)

print(create_answer(response_eng))
print(create_answer(response_span))
print(create_answer(response_fren))
print(create_answer(response_itan))