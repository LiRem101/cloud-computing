import boto3
from tabulate import tabulate

def grep_data():
    ec2 = boto3.client('ec2')
    return ec2.describe_regions()

def extract_endpoint_regionname(data: dict):
    list_of_regions = data['Regions']
    result = [['Endpoint', 'RegionName']]
    for region in list_of_regions:
        result.append([region['Endpoint'], region['RegionName']])
    return result

def print_table(data: list):
    print(tabulate(data, headers='firstrow'))

if __name__ == '__main__':
    data = grep_data()
    data_list = extract_endpoint_regionname(data)
    print_table(data_list)