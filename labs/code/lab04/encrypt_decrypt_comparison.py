from time import time

import boto3
import credentials as cred
import hashlib
import os
import struct

from Crypto import Random
from Crypto.Cipher import AES

BLOCK_SIZE = 16
CHUNK_SIZE = 64 * 1024
USER_ID = str(cred.STUD_NR)
ROOT_DIR = '.'
ROOT_S3_DIR = str(cred.STUD_NR) + '-cloudstorage'

s3 = boto3.client("s3")
kms = boto3.client('kms')

def encrypt_file_custom(password: str, in_filename: str):

    key = hashlib.sha256(password.encode("utf-8")).digest()

    iv = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    encrypted_content = b''
    with open(in_filename, 'rb') as infile:
        encrypted_content += struct.pack('<Q', filesize)
        encrypted_content += iv

        while True:
            chunk = infile.read(CHUNK_SIZE)
            if len(chunk) == 0:
                break
            elif len(chunk) % 16 != 0:
                chunk += ' '.encode("utf-8") * (16 - len(chunk) % 16)

            encrypted_content += encryptor.encrypt(chunk)

    return encrypted_content


def decrypt_file_custom(password: str, in_filename: str):

    key = hashlib.sha256(password.encode("utf-8")).digest()

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(in_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(CHUNK_SIZE)
                if len(chunk) == 0:
                    break
                write = decryptor.decrypt(chunk)
                outfile.write(write)

            #outfile.truncate(origsize)


def encrypt_file_kms(key_alias: str, in_filename: str):
    with open(in_filename, 'rb') as infile:
        content = infile.read(CHUNK_SIZE)
    encrypted_content = kms.encrypt(KeyId=key_alias, Plaintext=content)['CiphertextBlob']
    return encrypted_content


def decrypt_file_kms(key_alias: str, filename: str):
    with open(filename, 'rb') as outfile:
        filecontent = outfile.read()
    decrypted_content = kms.decrypt(CiphertextBlob=filecontent, KeyId=key_alias)['Plaintext']
    with open(filename, 'w') as outfile:
        outfile.write(bytes.decode(decrypted_content))



def upload_file(folder_name: str, file_path: str, file_name: str, key: str, kms: bool):
    print("Uploading %s" % file_path)
    start = time()
    if kms:
        encrypted_content = encrypt_file_kms(key_alias=key, in_filename=file_path)
    else:
        encrypted_content = encrypt_file_custom(password=key, in_filename=file_path)
    end = time()
    response = s3.put_object(Bucket=ROOT_S3_DIR, Body=encrypted_content, Key="/%s%s" % (folder_name, file_name))
    return end - start

def download_file(file_path: str, path: str, bucket_key: str, key: str, kms: bool):
    print("Downloading %s" % file_path)
    response = s3.get_object(Bucket=ROOT_S3_DIR, Key=bucket_key)
    filecontent = response['Body'].read()
    if not os.path.exists(path):
        os.makedirs(path)
    with open(file_path, 'wb') as file:
        file.write(filecontent)
    start = time()
    if kms:
        decrypt_file_kms(key_alias=key, filename=file_path)
    else:
        decrypt_file_custom(password=key, in_filename=file_path)
    end = time()
    return end - start



if __name__ == '__main__':
    key_alias = "alias/" + USER_ID
    password = 'password'
    folder_name = "/rootdir/"
    file_path = "../lab03/rootdir/rootfile.txt"
    file_name = "rootfile.txt"
    download_file_path = "../lab03/s3_restore/rootdir/rootfile.txt"
    download_path = "../lab03/s3_restore/rootdir/"
    print("Using kms...")
    encrypt_kms = upload_file(folder_name=folder_name, file_path=file_path, file_name=file_name, key=key_alias, kms=True)
    decrypt_kms = download_file(file_path=download_file_path, path=download_path,
                                bucket_key=folder_name + "rootfile.txt", key=key_alias, kms=True)
    print('KMS needed %0.3f ms to encrypt and %0.3f ms to decrypt.' % (encrypt_kms, decrypt_kms))
    print("Using custom solution...")
    encrypt_custom = upload_file(folder_name=folder_name, file_path=file_path, file_name=file_name, key=password,
                              kms=False)
    decrypt_custom = download_file(file_path=download_file_path, path=download_path,
                                bucket_key=folder_name + "rootfile.txt", key=password, kms=False)
    print('Custom solution needed %0.3f ms to encrypt and %0.3f ms to decrypt.' % (encrypt_custom, decrypt_custom))
