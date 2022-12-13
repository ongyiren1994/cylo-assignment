import boto3
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag_key", required=True)
    parser.add_argument("--tag_value", required=True)
    parser.add_argument("--profile_name", required=True)
    parser.add_argument("--region_name", required=True)
    args = parser.parse_args()
    tag_key = args.tag_key
    tag_value = args.tag_value
    profile_name = args.profile_name
    region_name = args.region_name

    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    client = session.client("ec2")

    paginator = client.get_paginator("describe_instances")
    operation_parameters = {"MaxResults": 100}
    page_iterator = paginator.paginate(**operation_parameters)
    security_group_ids = []
    for page in page_iterator:
        reservations = page["Reservations"]
        for reservation in reservations:
            instances = reservation["Instances"]
            for instance in instances:
                if {"Key": tag_key, "Value": tag_value} not in instance["Tags"]:
                    for security_group in instance["SecurityGroups"]:
                        security_group_ids.append(security_group["GroupId"])
    security_group_ids = list(set(security_group_ids))

    try:
        for security_group_id in security_group_ids:
            response = client.revoke_security_group_ingress(
                FromPort=22,
                ToPort=22,
                CidrIp="0.0.0.0/0",
                IpProtocol="tcp",
                GroupId=security_group_id,
            )
            if response["Return"]:
               if "UnknownIpPermissions" in response:
                  print("No insecure ssh rule within {0}".format(security_group_id))
               else:
                  print("Removed insecure ssh rule from {0}".format(security_group_id))
    except Exception as e:
        print(e)
