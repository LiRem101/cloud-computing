# Practical Worksheet 2
Version: 1.0 Date: 10/04/2018 Author: David Glance

Updated: 07/08/2022 Author: Dr Anwarul Patwary

## Learning Objectives
1. Create an EC2 instance, security group and ssh keys using awscli and python/boto
2. Configure VirtualBox to allow for inbound IP traffic
3. Install and configure Docker and run a hello world application that can be called from the host machine

## Technologies Covered

* Ubuntu
* AWS
* AWS EC2 Python/Boto/awscli/bash scripts VirtualBox
* Docker

Note: Do this from your VirtualBox VM – if you do it from any other platform (Windows, Mac – you will need to resolve any potential issues yourself)

## Create an EC2 instance using awscli
### [1] Create a security group

```
aws ec2 create-security-group --group-name <student number>-sg --description "security group for development environment"
```

![Security Group Creation.](images/create_security_group.png)

Note: this will use the default VPC (you will learn about this later in the course) – if you want to specify another VPC, you would use --vpc-id vpc-xxxxxxxx

Note the security group id that is created

### [2] Authorise inbound traffic for ssh

```
aws ec2 authorize-security-group-ingress --group-name <student number>-sg --protocol tcp --port 22 --cidr 0.0.0.0/0
```

![Authorise inbound traffic.](images/authorise_inbound_traffic.png)


### [3] Create a key pair that will allow you to ssh to the EC2 instance

```
aws ec2 create-key-pair --key-name <student number>-key --query 'KeyMaterial' --output text > <student number>-key.pem
```

![Create key pair.](images/create-key-pair.png)


To use this key on Linux, copy the file to a directory ~/.ssh and change the permissions to:

```
chmod 400 <student number>-key.pem
```

![Adapt keyfile to Linux.](images/keypair_to_ssh.png)


### [4] Create the instance and note the instance id

```
 aws ec2 run-instances --image-id ami-d38a4ab1 --security-group-ids <student number>-sg --count 1 --instance-type t2.micro --key-name <student number>-key --query 'Instances[0].InstanceId'

 ```

![Create Instance ID.](images/create-instance-id.png)


 Optional: Add a tag to your Instance
 ```
  aws ec2 create-tags --resources i-??????? --tags Key=Name,Value=<student number>
 ```

// 18.04 ami-176aa375


### [5] Get the public IP address

```
aws ec2 describe-instances --instance-ids i-<instance id from above> --query 'Reservations[0].Instances[0].PublicIpAddress'
```

![Get public ID.](images/public_id.png)


### [6] Connect to the instance
```
ssh -i <student number>-key.pem ubuntu@<IP Address>
```

![Connect to instance.](images/connect_to_instance.png)

### [7] Look at the instance using the AWS console

![Instances at AWS console.](images/instances_aws_console.png)

### [8] ****NOTE*****

Once you have finished, log onto the console and terminate the instance
or
```
aws ec2 terminate-instances --instance-ids i-<your instance id>
```

![Terminating the instance.](images/terminating_instance.png)


## Create an EC2 instance with Python Boto script

### [1] Repeat the steps above using the equivalent Boto commands in a python script. The script should output the IP address to connect to.


```
import boto3
import botocore.exceptions
import credentials as cred
import time


def create_group_and_key(ec2, groupname: str, keyname: str):
    try:
        ec2.create_security_group(GroupName=groupname, 
                                  Description="security group for development environment")
        ec2.authorize_security_group_ingress(GroupName=groupname, IpProtocol="tcp", FromPort=22,
                                            ToPort=22, CidrIp="0.0.0.0/0")
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
    instance = ec2.run_instances(ImageId="ami-d38a4ab1", SecurityGroupIds=[groupname],
                                MaxCount=1, MinCount=1, InstanceType='t2.micro', KeyName=keyname)
    instance_id = instance['Instances'][0]['InstanceId']
    # To give AWS the time to launch the instance.
    # Otherwise, the PublicIp is not available.
    time.sleep(1)
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
```

![Output of the Python code.](images/python_output_public_ip.png)


Optional: Create an EC2 instance using the console interface. Are there any differences from doing through the command line?

## Using Docker

### [1] Install Docker
```
sudo apt install docker.io -y
```

> Docker already installed.

You may have to

```
sudo systemctl start docker
sudo systemctl enable docker
```

### [2] Check the version

```
docker --version
```

![Docker Version.](images/docker_version.png)


### [3] Build and run an httpd container

Create a directory called html

Edit a file index.html inside the html directory and add the following content

```
  <html>
    <head> </head>
    <body>
      <p>Hello World!</p>
    </body>
  </html>
```

![Created index.html.](images/created_index_html.png)


### [4] Create a file called “Dockerfile” outside the html directory with the following content:

```
FROM httpd:2.4
COPY ./html/ /usr/local/apache2/htdocs/
```

![Created Dockerfile.](images/Dockerfile_content.png)

### [5] Build the docker image

```
docker build -t my-apache2 .
```

![Build.](images/docker-build.png)


If you run into permission errors, you may need add your user to the docker group:

```
sudo usermod -a -G docker <username>
```

Be sure to log out and log back in for this change to take effect.

### [6] Run the image

```
docker run -p 80:80 -dit --name my-app my-apache2
```

![Run.](images/docker-run.png)


### [7] Open a browser and access address http://localhost or http://127.0.0.1 Confirm you get Hello World!

![Hello World at localhost.](images/docker-hello-world.png)

### [8] Other commands

To check what is running

```
docker ps -a
```

![See what is running.](images/docker-ps-a.png)

To stop and remove the container

```
docker stop my-app
docker rm my-app
```

![Stop and delete container.](images/docker-delete.png)


Lab Assessment:

This semester all labs will be assessed as "Lab notes". You should follow all steps in each lab and include your own comments. In addition, include screenshots showing the output for every commandline instruction that you execute in the terminal and any other relevant screenshots that demonstrate you followed the steps from the corresponding lab. Please also include any linux or python script that you create and the corresponding output you get when executed.
Please submit a single PDF file. The formatting is up to you but a well organised structure of your notes is appreciated.

Please include the content of the files index.html, Dockerfile and the rest of linux commands in the document.
