import json
import os
import boto3
import botocore.exceptions
import stat
import sys
import credentials as cred
import pwd
import time

ROOT_DIR = '.'
ROOT_S3_DIR = str(cred.STUD_NR) + '-cloudstorage'
IGNORED = ['./s3_restore', './__', './dynamodb']
USER_ID = str(cred.STUD_NR)

s3 = boto3.client("s3")
kms = boto3.client('kms')
dynamodb = boto3.client('dynamodb', endpoint_url='http://localhost:8000')

def upload_file(folder_name, file, file_name):
    item_from_db = dynamodb.get_item(TableName="CloudFiles",
                                     Key={'userId': {'S': USER_ID}, 'fileName': {'S': file_name}})
    stats = os.stat(file)
    permissions = stat.filemode(stats.st_mode)
    owner = pwd.getpwuid(stats.st_uid).pw_name
    last_updated = time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.gmtime(stats.st_mtime))
    if 'Item' in item_from_db and last_updated == item_from_db['Item']['lastUpdated']['S']:
        print("File has not been changed since last upload.")
        return
    print("Uploading %s" % file)
    try:
        with open(file, 'r') as file:
            key_alias = "alias/" + USER_ID
            encrypted_content = kms.encrypt(KeyId=key_alias, Plaintext=bytes(file.read(), 'utf-8'))['CiphertextBlob']
            print("Decrypted content into %s" % encrypted_content)
            response = s3.put_object(Bucket=ROOT_S3_DIR, Body=encrypted_content, Key="/%s%s" % (folder_name, file_name))
            print(response)
            dynamodb.put_item(TableName='CloudFiles',
                              Item={'userId': {'S': USER_ID}, 'fileName': {'S': file_name}, 'path': {'S': folder_name},
                                    'lastUpdated': {'S': last_updated}, 'owner': {'S': owner},
                                    'permissions': {'S': permissions}})
    except Exception as error:
        print("Error: " + str(error))


def create_bucket(bucket_config: dict):
    try:
        response = s3.create_bucket(Bucket=ROOT_S3_DIR, CreateBucketConfiguration=bucket_config)
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            response = "Bucket already existed."
        else:
            raise error
    policy = {"Version": "2012-10-17",
              "Statement": {
                  "Sid": "AllowAllS3ActionsInUserFolderForUserOnly",
                  "Effect": "DENY",
                  "Principal": "*",
                  "Action": "s3:*",
                  "Resource": f'arn:aws:s3:::{ROOT_S3_DIR}/*',
                  "Condition": {
                      "StringNotLike": {
                          "aws:username": f'{str(USER_ID)}@student.uwa.edu.au'}}}}
    policy = json.dumps(policy)
    s3.put_bucket_policy(Bucket=ROOT_S3_DIR, Policy=policy)
    print(response)


# parse directory and upload files
def upload_files():
    for dir_name, subdir_list, file_list in os.walk(ROOT_DIR, topdown=True):
        if dir_name != ROOT_DIR and not any(list(map(dir_name.startswith, IGNORED))):
            for fname in file_list:
                upload_file("%s/" % dir_name[2:], "%s/%s" % (dir_name, fname), fname)

    print("done")


if __name__ == '__main__':
    bucket_config = {'LocationConstraint': 'ap-southeast-2'}
    if '-i' in sys.argv or '--initialise=True' in sys.argv:
        create_bucket(bucket_config)
        upload_files()
