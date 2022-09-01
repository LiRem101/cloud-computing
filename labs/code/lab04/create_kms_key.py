import boto3
import credentials as cred
import json

USER_ID = str(cred.STUD_NR)
KEY_POLICY = {
    "Version": "2012-10-17",
    "Id": "key-consolepolicy-3",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::523265914192:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow access for Key Administrators",
            "Effect": "Allow",
            "Principal": {
                "AWS": f'arn:aws:iam::523265914192:user/{USER_ID}@student.uwa.edu.au'
            },
            "Action": [
                "kms:Create*",
                "kms:Describe*",
                "kms:Enable*",
                "kms:List*",
                "kms:Put*",
                "kms:Update*",
                "kms:Revoke*",
                "kms:Disable*",
                "kms:Get*",
                "kms:Delete*",
                "kms:TagResource",
                "kms:UntagResource",
                "kms:ScheduleKeyDeletion",
                "kms:CancelKeyDeletion"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Allow use of the key",
            "Effect": "Allow",
            "Principal": {
                "AWS": f'arn:aws:iam::523265914192:user/{USER_ID}@student.uwa.edu.au'
            },
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Allow attachment of persistent resources",
            "Effect": "Allow",
            "Principal": {
                "AWS": f'arn:aws:iam::523265914192:user/{USER_ID}@student.uwa.edu.au'
            },
            "Action": [
                "kms:CreateGrant",
                "kms:ListGrants",
                "kms:RevokeGrant"
            ],
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "kms:GrantIsForAWSResource": "true"
                }
            }
        }
    ]
}

kms = boto3.client('kms')

# parse directory and upload files
def create_key():
    key_policy = json.dumps(KEY_POLICY)
    response = kms.create_key(Policy=key_policy)
    kms.create_alias(AliasName="alias/" + USER_ID, TargetKeyId=response['KeyMetadata']['KeyId'])
    print(response)


if __name__ == '__main__':
    create_key()
