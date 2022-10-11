import boto3
from iso639 import languages

def entities_analysis(text):
    language_code = client.detect_dominant_language(Text=text, )['Languages'][0]['LanguageCode']
    entities = client.detect_entities(Text=text, LanguageCode=language_code)['Entities']
    language_name = languages.get(alpha2=language_code).name
    entities = [x['Text'] for x in entities]
    return "The " + language_name + " text has the entites:" + str(entities)

client = boto3.client('comprehend')

eng = "The French Revolution was a period of social and political upheaval in France and its colonies beginning in 1789 and ending in 1799."
span = "El Quijote es la obra más conocida de Miguel de Cervantes Saavedra. Publicada su primera parte con el título de El ingenioso hidalgo don Quijote de la Mancha a comienzos de 1605, es una de las obras más destacadas de la literatura española y la literatura universal, y una de las más traducidas. En 1615 aparecería la segunda parte del Quijote de Cervantes con el título de El ingenioso caballero don Quijote de la Mancha."
fren = "Moi je n'étais rien Et voilà qu'aujourd'hui Je suis le gardien Du sommeil de ses nuits Je l'aime à mourir Vous pouvez détruire Tout ce qu'il vous plaira Elle n'a qu'à ouvrir L'espace de ses bras Pour tout reconstruire Pour tout reconstruire Je l'aime à mourir"
itan = "L'amor che move il sole e l'altre stelle."

print(entities_analysis(eng))
print(entities_analysis(span))
print(entities_analysis(fren))
print(entities_analysis(itan))