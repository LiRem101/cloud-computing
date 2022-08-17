import os
import boto3
import botocore.exceptions
import base64
import sys
import credentials as cred

ROOT_DIR = '.'
ROOT_S3_DIR = str(cred.STUD_NR) + '-cloudstorage'

def upload_file(folder_name, file, file_name):
    print("Uploading %s" % file)
    try:
        response = s3.upload_file(Filename=file, Bucket=ROOT_S3_DIR, Key="/%s%s" % (folder_name, file_name))
        print(response)
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
    print(response)

# parse directory and upload files
def upload_files():
    for dir_name, subdir_list, file_list in os.walk(ROOT_DIR, topdown=True):
        if dir_name != ROOT_DIR and not dir_name.startswith("./__"):
            for fname in file_list:
                upload_file("%s/" % dir_name[2:], "%s/%s" % (dir_name, fname), fname)

    print("done")


if __name__ == '__main__':
    s3 = boto3.client("s3")
    bucket_config = {'LocationConstraint': 'ap-southeast-2'}
    if('-i' in sys.argv or '--initialise=True' in sys.argv):
        create_bucket(bucket_config)
        upload_files()
    else:
        print(s3.delete_object(Bucket=ROOT_S3_DIR, Key='rootfile.txt'))
        print(s3.delete_object(Bucket=ROOT_S3_DIR, Key='subfile.txt'))
        print(s3.delete_bucket(Bucket=ROOT_S3_DIR))