import boto3
import credentials as cred

def label_recognition(bucket, file):
    image = {'S3Object': {'Bucket': bucket, 'Name': file}}
    labels = client.detect_labels(Image=image)['Labels']
    labels = [x['Name'] for x in labels]
    return "Labels of " + file + ":" + str(labels)

def moderation(bucket, file):
    image = {'S3Object': {'Bucket': bucket, 'Name': file}}
    labels = client.detect_moderation_labels(Image=image)['ModerationLabels']
    labels = [x['Name'] for x in labels]
    return "Moderation labels of " + file + ":" + str(labels)

def facial_string(attribute):
    face = "The face shows a person between " + str(attribute['AgeRange']['Low']) + " and " \
            + str(attribute['AgeRange']['High']) + ". They are " + str(attribute['Gender']['Value']) + ", "
    if not attribute['Smile']['Value']:
        face += "not "
    face += "smiling, "
    if not attribute['Eyeglasses']['Value']:
        face += "not "
    face += "wearing eyeglasses and "
    if not attribute['Sunglasses']['Value']:
        face += "not "
    face += "wearing sunglasses. They do "
    if not attribute['Beard']['Value']:
        face += "not "
    face += "have a beard and "
    if not attribute['Mustache']['Value']:
        face += "no "
    face += "mustache. Their eyes are "
    if attribute['EyesOpen']['Value']:
        face += "open "
    else:
        face += "closed "
    face += "and their mouth is "
    if attribute['MouthOpen']['Value']:
        face += "open. "
    else:
        face += "closed. "
    face += "Their main emotions are "
    for e in attribute['Emotions']:
        if e['Confidence'] > 90:
            face += str.lower(e['Type']) + ", "
    face = face[:-2]
    face += "."
    return face

def facial_analysis(bucket, file):
    image = {'S3Object': {'Bucket': bucket, 'Name': file}}
    attributes = client.detect_faces(Image=image, Attributes=["ALL"])['FaceDetails']
    answer_string = []
    for a in attributes:
        answer_string.append(facial_string(a))
    return answer_string

def extract_text(bucket, file):
    image = {'S3Object': {'Bucket': bucket, 'Name': file}}
    text = client.detect_text(Image=image)['TextDetections'][0]['DetectedText']
    return "The text on " + file + " is: \"" + text + "\"."


client = boto3.client('rekognition')

student_id = str(cred.STUD_NR)
bucket = student_id + "-lab09"
urban = "urban.jpg"
beach = "beach.jpg"
face = "faces.jpg"
text = "text.jpg"

print(label_recognition(bucket, urban))
print(moderation(bucket, beach))
face_strings = facial_analysis(bucket, face)
print("Result of facial analysis of " + face + ":")
for f in face_strings:
    print(f)
print(extract_text(bucket, text))