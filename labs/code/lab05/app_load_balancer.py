import boto3
import credentials as cred
import time


def create_instance(ec2, groupname: str, availablity_zone: str, stud_nr: str):
    name = stud_nr + "_" + availablity_zone
    instance = ec2.run_instances(ImageId="ami-d38a4ab1", SecurityGroupIds=[groupname], MaxCount=1, MinCount=1,
                                 InstanceType='t2.micro', KeyName=keyname,
                                 Placement={'AvailabilityZone': availablity_zone},
                                 TagSpecifications=[{'ResourceType': 'instance',
                                                     'Tags': [{'Key': 'Name', 'Value': name}, ]}, ], )
    return instance['Instances'][0]['InstanceId']


def wait_until_instances_are_running(instance_ids):
    ec2_r = boto3.resource('ec2')
    for id in instance_ids:
        ec2_r.Instance(id).wait_until_running()


def security_group_id(ec2, group_name: str):
    response = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [group_name]}])
    return response['SecurityGroups'][0]['GroupId']


def create_load_balancer(elbv2):
    lb_name = str(student_nr) + "-lb"
    group_id = security_group_id(ec2, groupname)
    subnets = ec2.describe_subnets(Filters=[{'Name': 'availability-zone', 'Values': [zone_a, zone_b]}])['Subnets']
    subnet_ids = []
    for s in subnets:
        subnet_ids.append(s['SubnetId'])
    balancer = elbv2.create_load_balancer(Name=lb_name, Subnets=subnet_ids, SecurityGroups=[group_id])['LoadBalancers'][0]
    balancer_arn = balancer['LoadBalancerArn']
    balancer_dns = balancer['DNSName']
    return balancer_arn, balancer_dns


def create_listener(ec2, elbv2):
    vpc_id = ec2.describe_vpcs()['Vpcs'][0]['VpcId']
    target_group_name = str(student_nr) + "-tg"
    target_arn = elbv2.create_target_group(Name=target_group_name, Protocol='HTTP',
                                           Port=80, VpcId=vpc_id)['TargetGroups'][0]['TargetGroupArn']
    elbv2.register_targets(TargetGroupArn=target_arn, Targets=[{'Id': instance_a_id}, {'Id': instance_b_id}])
    elbv2.create_listener(LoadBalancerArn=balancer_arn, Protocol='HTTP', Port=80,
                          DefaultActions=[{'Type': 'forward', 'TargetGroupArn': target_arn}])


def get_public_ip(ec2, instance_ids):
    inst_descriptions = ec2.describe_instances(InstanceIds=instance_ids)['Reservations']
    ips = []
    for i in inst_descriptions:
        ips.append(i['Instances'][0]['PublicIpAddress'])
    return ips

if __name__ == '__main__':
    student_nr = cred.STUD_NR
    ec2 = boto3.client('ec2')
    groupname = str(student_nr) + "-sg"
    keyname = str(student_nr) + "-key"
    zone_a = "ap-southeast-2a"
    zone_b = "ap-southeast-2b"

    instance_a_id = create_instance(ec2, groupname, zone_a, str(student_nr))
    instance_b_id = create_instance(ec2, groupname, zone_b, str(student_nr))

    wait_until_instances_are_running([instance_a_id, instance_b_id])
    ips = get_public_ip(ec2, [instance_a_id, instance_b_id])
    print('Instances with following public ips have been created: ' + str(ips))

    elbv2 = boto3.client('elbv2')
    balancer_arn, balancer_dns = create_load_balancer(elbv2)
    create_listener(ec2, elbv2)
    print('Access via ' + balancer_dns)

