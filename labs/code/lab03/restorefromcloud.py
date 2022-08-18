import os
import boto3
import credentials as cred

ROOT_DIR = '.'
ROOT_S3_DIR = str(cred.STUD_NR) + '-cloudstorage'

def restore_file(file_name: str):
    print("Downloading %s" % file_name)
    filecontent = b''
    try:
        response = s3.get_object(Bucket=ROOT_S3_DIR, Key=file_name)
        filecontent = response['Body']
    except Exception as error:
        print("Error: " + str(error))

    path = './s3_restore' + '/'.join(file_name.split('/')[:-1])

    if not os.path.exists(path):
        os.makedirs(path)
    with open(str("./s3_restore" + file_name), 'w') as file:
        file.write(bytes.decode(filecontent.read()))


# parse directory and upload files
def restore_files():
    for content in s3.list_objects_v2(Bucket=ROOT_S3_DIR)['Contents']:
       restore_file(file_name=content['Key'])
    print("done")


if __name__ == '__main__':
    s3 = boto3.client("s3")
    bucket_config = {'LocationConstraint': 'ap-southeast-2'}
    restore_files()