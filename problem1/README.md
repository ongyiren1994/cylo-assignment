# Documentation

## VPC Setup
1. All resources would be created within a single VPC.
2. Create 8 subnets in total, for the following purposes.
   - ALB would be provisioned in 2 public subnets in different AZs.
   - EC2 instances (which host applications) would be provisioned in two private subnets in different AZs via Auto Scaling Group.
   - Redis instances would be provisioned in two private subnets in different AZs.
   - RDS instances would be provisioned in two private subnets in different AZs.
3. Create 2 NAT gateways in each public subnets to allow egress traffics for EC2 instances.
4. Attach a single Internet Gateway to the VPC.

## EC2 Launch Template
1. [Launch an EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-instance-wizard.html) within the private subnet.
2. [Associate an Instance profile](https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-instance-profile.html) with that EC2 instance so that it could be accessed via SSM and not SSH.
3. Login to the EC2 instance via SSM and install [AWS CloudWatch Agent](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html).Create custom monitoring script to [push the custom metrics (such as Memory Usage) periodically](https://aws.amazon.com/premiumsupport/knowledge-center/cloudwatch-push-custom-metrics/) to CloudWatch via CloudWatch Agent.
4. Install the applications.
5. Stop the instance and [create an AMI from the EC2 Instance](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/tkv-create-ami-from-instance.html).
5. [Create a launch template for Auto Scaling Group](https://docs.aws.amazon.com/autoscaling/ec2/userguide/create-launch-template.html) using the new AMI.

## Auto Scaling Group
1. [Creating the Auto Scaling Group using the launch template](https://docs.aws.amazon.com/autoscaling/ec2/userguide/create-asg-launch-template.html).
2. Configure Auto Scaling Group to [scale based on memories usage of instances](https://aws.amazon.com/blogs/mt/create-amazon-ec2-auto-scaling-policy-memory-utilization-metric-linux/#:~:text=Open%20the%20Amazon%20EC2%20console,Create%20an%20Auto%20Scaling%20group).

## Load Balancing
1. ALB is chosen to load balance the HTTPS traffics.
2. [Sticky sessions](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/sticky-sessions.html) approach is chosen to provide a continuous experience to clients.
3. [Configure ALB to perform TLS termination](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html).
4. [Associate AWS WAF with ALB](https://docs.amazonaws.cn/en_us/AmazonCloudFront/latest/DeveloperGuide/distribution-web-awswaf.html) to prevent malicious attack.

## Route Entries
1. Create route tables and associate the following subnets with the following entries
    - EC2 private subnets
      - 0.0.0.0 -> NAT Gateway ID (varies depends on AZ)
    - ALB public subnets
      - 0.0.0.0 -> Internet Gateway ID
    - Elasticache private subnets (Use default route entries)
    - RDS private subnets (Use default route entries)

## Security Groups
1. Create security groups and configure the rules as follow
    - EC2 instances
      - Inbound
        - Allow HTTP traffic from ALB
      - Outbound
        - Allow Redis traffic to Elasticache
        - Allow PostgreSQL traffic to RDS
        - Allow ALL traffic to Internet
    - ALB
      - Inbound
        - Allow HTTPS traffic from Internet
        - Allow HTTP traffic from Internet
      - Outbound
        - Allow HTTP traffic to EC2 instances
    - Elasticache
      - Inbound
        - Allow Redis traffic from EC2 instances
      - Outbound
        - None
    - RDS
      - Inbound
        - Allow PostgreSQL traffic from EC2 instances
      - Outbound
        - None

## NACL
1. Create NACLs and associate the following subnets with the following rules
    - EC2 private subnets
      - Inbound
        - Allow HTTP traffic from ALB
        - Allow returning Redis traffic from Elasticache
        - Allow returning PostgreSQL traffic from RDS
        - Allow ALL traffic to Internet
      - Outbound
        - Allow Redis traffic to Elasticache
        - Allow PostgreSQL traffic to RDS
        - Allow ALL traffic to Internet
        - Allow returning HTTP traffic to ALB
    - ALB public subnets
      - Inbound
        - Allow HTTPS traffic from Internet
        - Allow HTTP traffic from Internet
        - Allow returning HTTP traffic from EC2 instances
      - Outbound
        - Allow HTTP traffic to EC2 instances
        - Allow returning HTTPS traffic to internet
        - Allow returning HTTP traffic to internet
    - Elasticache private subnets
      - Inbound
        - Allow Redis traffic from EC2 instances
      - Outbound
        - Allow returning Redis traffic to EC2 instances
    - RDS private subnets
      - Inbound
        - Allow PostgreSQL traffic from EC2 instances
      - Outbound
        - Allow returning PostgreSQL traffic to EC2 instances

## Alerts
1. Configure [SNS](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-sns-notifications.html) to allow CloudWatch to send notifications to it when CloudWatch Alarm threshold is triggered.
2. [Subscribe to the corresponding SNS topic](https://docs.aws.amazon.com/sns/latest/dg/sns-create-subscribe-endpoint-to-topic.html) via emails to receive the alart notifications.
3. [Configure CloudWatch Alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ConsoleAlarms.html) based on CPU metrics, Memory metrics and etc.

## Backup Policies
1. Utilize [AWS Backup](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_backup_best-practices.html) to perform backup.

## S3
1. Create a S3 buckets and put the static contents into the buckets.
2. [Ensure S3 is secured](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html).

## Route53
1. Create a [Route53 hosted zone](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingHostedZone.html).
2. Create records to [point to CloudFront](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-cloudfront-distribution.html).

## CloudFront
1. Create a single [CloudFront web distribution](https://aws.amazon.com/premiumsupport/knowledge-center/cloudfront-distribution-serve-content/) to serve
   - Static contents from S3 buckets
   - Dynamic contents from ALB
2. [Associate AWS WAF with CloudFront](https://docs.amazonaws.cn/en_us/AmazonCloudFront/latest/DeveloperGuide/distribution-web-awswaf.html) to prevent malicious attack.

## RDS
1. Create a [Multi-AZ RDS](https://aws.amazon.com/rds/features/multi-az/) to ensure HA. PostgreSQL is chosen.
2. [Distribute read requests across multiple Amazon RDS read replicas](https://aws.amazon.com/premiumsupport/knowledge-center/requests-rds-read-replicas/).

## ElastiCache
1. Create a [Redis Cluster](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Clusters.Create.html).

## CI/CD
1. The infrastracture would be provisioned via [Terraform](https://developer.hashicorp.com/terraform/intro).
2. The Terraform source code would be stored in Github repository.
3. Setup [OpenID Connect](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services) within Github workflows to authenticate with Amazon Web Services.
4. Setup [Atlantis](https://www.runatlantis.io/docs/installation-guide.html) to run Terraform.
5. Work should never be done in `master` branch.
Instead of working in `master`, changes should be merged in via Pull Requests from other feature branches.
6. After the PR is raised, run `atlantis plan` to review the changes and seek approval from others.
7. Once the minimal number of PR approval reaches, developer can run `atlantis apply` to deploy the infrastracture and merge the branch back to `master`.