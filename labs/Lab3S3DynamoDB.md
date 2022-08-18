# Practical Worksheet 3

Version: 1.0 Date: 12/04/2018 Author: David Glance

Updated Date: 14/08/2022 Author: Anwarul Patwary

## Learning Objectives

1.	Learn how to create and configure S3 buckets and read and write objects to them
2.	Learn how to use operations on DynamoDB: Create table, put items, get items
3.	Start an application is your own personal Cloud Storage

## Technologies Covered

* Ubuntu
* AWS
* AWS S3
* AWS DynamoDB
* Python/Boto scripts
* VirtualBox

Note: Do this from your VirtualBox VM – if you do it from any other platform (Windows, Mac – you will need to resolve any potential issues yourself)

## Background

The aim of this lab is to write a program that will:

[1] Scan a directory and upload all of the files found in the directory to an S3 bucket, preserving the path information
[2] Store information about each file uploaded to S3 in a DynamoDB
[3] Restore the directory on a local drive using the files in S3 and the information in DynamoDB

## Program

### [Step 1] Preparation

Download the python code cloudstorage.py from https://github.com/dglance/cits5503/blob/master/Labs/src/cloudstorage.py \
Create a directory rootdir \
Create a file in rootdir called rootfile.txt and put some content in it “1\n2\n3\n4\n5\n”

Create a second directory in rootdir called subdir and create another file subfile.txt with the same content as rootfile.txt

![Preparation done.](images/lab03_prepare_directories.png)

### [Step 2] Save to S3

Edit cloudstorage.py to take one argument: -i, --initialise=True – this will use boto to create a bucket on S3 that is identified by \<student number>-cloudstorage

Insert boto commands to save each file that is found as the program traverses the directory starting at the root directory rootdir.

NOTE the easiest way to upload files is to use the command:

```
s3.upload_file()
```

```
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
        response = s3.upload_file(Filename=file, Bucket=ROOT_S3_DIR, 
                                  Key="/%s%s" % (folder_name, file_name))
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
                print("%s/" % dir_name[2:] + " " +"%s/%s" % (dir_name, fname) + " " + fname)
                upload_file("%s/" % dir_name[2:], "%s/%s" % (dir_name, fname), fname)

    print("done")


if __name__ == '__main__':
    s3 = boto3.client("s3")
    bucket_config = {'LocationConstraint': 'ap-southeast-2'}
    if('-i' in sys.argv or '--initialise=True' in sys.argv):
        create_bucket(bucket_config)
        upload_files()
```

![Results of the Python program.](images/lab3_s3_save.png)


### [Step 3] Restore from S3

Create a new program called restorefromcloud.py that reads the S3 bucket and writes the contents of the bucket within the appropriate directories. You should have a copy of the files and the directories you started with.

```
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
```

![Restore S3 files via Python code.](images/lab03_restore_files.png)

### [Step 4] Write information about files to DynamoDB
Install DynamoDB on your VM.

```
mkdir dynamodb;
cd dynamodb
```

Install jre if not done

```
sudo apt-get install default-jre
```

```
wget https://s3-ap-northeast-1.amazonaws.com/dynamodb-local-tokyo/dynamodb_local_latest.tar.gz
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar –sharedDb
```

Or you can use docker as we discussed in Week 2:
```
docker run -p 8000:8000 amazon/dynamodb-local -jar DynamoDBLocal.jar -inMemory -sharedDb
```

Create a table on your local DynamoDB with the key userId
The attributes for the table will be:

```
        CloudFiles = {
            'userId',
            'fileName',
            'path',
            'lastUpdated',
	    'owner',
            'permissions'
            }
        )
```

For every file that is stored in S3, get the information to put in the DynamoDB item and write it to the table. You will have to find functions in Python to get details like time lastUpdated, owner and permissions. All of this information can be stored as strings.

### [Step 5] Optional
Add the functionality to apply changes to permissions and ownership when the directory and files are restored.
Check timestamps on files and only upload if the file has been updated.

Lab Assessment:
This semester all labs will be assessed as "Lab notes". You should follow all steps in each lab and include your own comments. In addition, include screenshots showing the output for every commandline instruction that you execute in the terminal and any other relevant screenshots that demonstrate you followed the steps from the corresponding lab. Please also include any linux or python script that you create and the corresponding output you get when executed.
Please submit a single PDF file. The formatting is up to you but a well organised structure of your notes is appreciated.


