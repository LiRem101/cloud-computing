import os
import boto3
import credentials as cred
import pwd
import stat
import sys

ROOT_DIR = '.'
ROOT_S3_DIR = str(cred.STUD_NR) + '-cloudstorage'


def create_permission_logic(permissions: str):
    p_arg = False
    if permissions[0] == 'r':
        p_arg = p_arg | stat.S_IRUSR
    if permissions[1] == 'w':
        p_arg = p_arg | stat.S_IWUSR
    if permissions[2] == 'x':
        p_arg = p_arg | stat.S_IXUSR
    if permissions[3] == 'r':
        p_arg = p_arg | stat.S_IRGRP
    if permissions[4] == 'w':
        p_arg = p_arg | stat.S_IWGRP
    if permissions[5] == 'x':
        p_arg = p_arg | stat.S_IXGRP
    if permissions[6] == 'r':
        p_arg = p_arg | stat.S_IROTH
    if permissions[7] == 'w':
        p_arg = p_arg | stat.S_IWOTH
    if permissions[8] == 'x':
        p_arg = p_arg | stat.S_IXOTH
    return p_arg


def restore_file(file_name: str, owner: str, permissions: str):
    print("Downloading %s" % file_name)
    filecontent = b''
    try:
        response = s3.get_object(Bucket=ROOT_S3_DIR, Key=file_name)
        filecontent = response['Body']
    except Exception as error:
        print("Error: " + str(error))

    if not owner == "":
        # Checking uid here to abort if not fitting user exists
        # before anything is actually pulled out of bucket
        uid = pwd.getpwnam(owner).pw_uid
    if not permissions == "":
        p_arg = create_permission_logic(permissions)

    path = './s3_restore' + '/'.join(file_name.split('/')[:-1])

    if not os.path.exists(path):
        os.makedirs(path)
    with open(str("./s3_restore" + file_name), 'w') as file:
        file.write(bytes.decode(filecontent.read()))

    if not owner == "":
        os.chown(str("./s3_restore" + file_name), uid, -1)
    if not permissions == "":
        os.chmod(str("./s3_restore" + file_name), p_arg)


# parse directory and upload files
def restore_files(owner: str, permissions: str):
    objects_of_bucket = s3.list_objects_v2(Bucket=ROOT_S3_DIR)
    if 'Contents' in objects_of_bucket:
        for content in objects_of_bucket['Contents']:
            restore_file(file_name=content['Key'], owner=owner, permissions=permissions)
    print("done")


if __name__ == '__main__':
    s3 = boto3.client("s3")
    bucket_config = {'LocationConstraint': 'ap-southeast-2'}
    owner = ""
    permissions = ""
    if '--owner' in sys.argv:
        i = sys.argv.index('--owner') + 1
        if len(sys.argv) > i:
            owner = sys.argv[i]
        else:
            raise Exception("--owner needs a parameter.")
    if '--permissions' in sys.argv:
        i = sys.argv.index('--permissions') + 1
        if len(sys.argv) > i:
            permissions = sys.argv[i]
        else:
            raise Exception("--permissions needs a parameter.")
    restore_files(owner=owner, permissions=permissions)
