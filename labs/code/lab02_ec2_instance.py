import boto3
import botocore.exceptions
import credentials as cred
import time


def create_group_and_key(ec2, groupname: str, keyname: str):
    try:
        ec2.create_security_group(GroupName=groupname, Description="security group for development environment")
        ec2.authorize_security_group_ingress(GroupName=groupname, IpProtocol="tcp", FromPort=22, ToPort=22,
                                             CidrIp="0.0.0.0/0")
    except botocore.exceptions.ClientError:
        print("Group already existed.")

    try:
        key = ec2.create_key_pair(KeyName=keyname)
        with open(cred.KEY_FIlE, "w") as f:
            f.write("-----BEGIN RSA PRIVATE KEY-----\n")
            f.write(key['KeyMaterial'])
            f.write("-----END RSA PRIVATE KEY-----\n")
    except botocore.exceptions.ClientError:
        print("Key already existed.")


def get_public_ip_address(ec2, groupname: str):
    instance = ec2.run_instances(ImageId="ami-d38a4ab1", SecurityGroupIds=[groupname], MaxCount=1, MinCount=1,
                                 InstanceType='t2.micro', KeyName=keyname)
    instance_id = instance['Instances'][0]['InstanceId']
    time.sleep(1) # To give AWS the time to launch the instance. Otherwise, the PublicIp is not available.
    inst_description = ec2.describe_instances(InstanceIds=[instance_id])
    publicId = inst_description['Reservations'][0]['Instances'][0]['PublicIpAddress']
    return publicId


if __name__ == '__main__':
    student_nr = cred.STUD_NR
    ec2 = boto3.client('ec2')
    groupname = str(student_nr) + "-sg"
    keyname = str(student_nr) + "-key"
    create_group_and_key(ec2, groupname, keyname)
    publicIp = get_public_ip_address(ec2, groupname)
    print("Public IP address is " + publicIp)