#!/usr/bin/env python3
"""
AnyDown — One-Click AWS EC2 Deployment Tool
Deploys Frontend, Backend, and Nginx reverse proxy to AWS EC2 using boto3.
"""

import sys
import os
import time
import tarfile
import subprocess
import shutil
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import NoCredentialsError, ClientError
except ImportError:
    print("[ERROR] boto3 is not installed. Run: python -m pip install boto3")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent

def print_header():
    print("=" * 60)
    print("       AnyDown — AWS EC2 One-Click Deployment")
    print("=" * 60)

def verify_credentials():
    print("\n[1/6] Verifying AWS credentials...")
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        print(f"      Authenticated as IAM Identity: {identity['Arn']}")
        return identity
    except NoCredentialsError:
        print("\n[ERROR] No AWS credentials found!")
        print("Please configure your credentials by running:")
        print("    aws configure")
        print("(or: python -m awscli configure)")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Authentication failed: {e}")
        print("Please check your AWS credentials via 'aws configure'.")
        sys.exit(1)

def get_region():
    session = boto3.session.Session()
    region = session.region_name or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"
    print(f"      Target AWS Region: {region}")
    return region

def ensure_key_pair(ec2_client, key_name="anydown-ec2-key"):
    print("\n[2/6] Checking EC2 Key Pair...")
    key_file = PROJECT_ROOT / f"{key_name}.pem"

    try:
        ec2_client.describe_key_pairs(KeyNames=[key_name])
        print(f"      Key Pair '{key_name}' already exists in AWS.")
        if not key_file.exists():
            print(f"      [WARNING] Local private key '{key_file}' not found.")
            print(f"      If you lost this key, delete it in AWS or run:")
            print(f"      python -m awscli ec2 delete-key-pair --key-name {key_name}")
            sys.exit(1)
    except ClientError as e:
        if "InvalidKeyPair.NotFound" in str(e):
            print(f"      Creating new Key Pair '{key_name}'...")
            resp = ec2_client.create_key_pair(KeyName=key_name, KeyType="rsa")
            key_material = resp["KeyMaterial"]
            with open(key_file, "w", encoding="ascii") as f:
                f.write(key_material)
            print(f"      Saved private key to: {key_file}")
        else:
            raise

    # Secure permissions on Windows / POSIX
    try:
        if os.name == "nt":
            username = os.environ.get("USERNAME", "Everyone")
            subprocess.run(
                ["icacls.exe", str(key_file), "/inheritance:r", f"/grant:r", f"{username}:(R)"],
                capture_output=True, check=False
            )
        else:
            key_file.chmod(0o400)
    except Exception:
        pass

    return key_file

def ensure_security_group(ec2_client, sg_name="anydown-ec2-sg"):
    print(f"\n[3/6] Checking Security Group '{sg_name}'...")
    try:
        resp = ec2_client.describe_security_groups(GroupNames=[sg_name])
        sg_id = resp["SecurityGroups"][0]["GroupId"]
        print(f"      Security Group '{sg_name}' already exists ({sg_id}).")
        return sg_id
    except ClientError as e:
        if "InvalidGroup.NotFound" in str(e):
            print(f"      Creating Security Group '{sg_name}'...")
            resp = ec2_client.create_security_group(
                GroupName=sg_name,
                Description="AnyDown Security Group (HTTP/HTTPS/SSH)"
            )
            sg_id = resp["GroupId"]

            print("      Authorizing ports 22 (SSH), 80 (HTTP), 443 (HTTPS)...")
            ip_permissions = [
                {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
                {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
                {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
            ]
            ec2_client.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=ip_permissions)
            return sg_id
        else:
            raise

def get_ubuntu_ami(region):
    print(f"\n[4/6] Resolving latest Ubuntu 24.04 LTS AMI in {region}...")
    ssm = boto3.client("ssm", region_name=region)
    try:
        param = ssm.get_parameter(
            Name="/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
        )
        ami_id = param["Parameter"]["Value"]
        print(f"      Selected AMI: {ami_id}")
        return ami_id
    except Exception:
        ec2 = boto3.client("ec2", region_name=region)
        resp = ec2.describe_images(
            Owners=["099720109477"],
            Filters=[
                {"Name": "name", "Values": ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]},
                {"Name": "state", "Values": ["available"]}
            ]
        )
        images = sorted(resp["Images"], key=lambda x: x["CreationDate"], reverse=True)
        ami_id = images[0]["ImageId"]
        print(f"      Selected AMI (fallback): {ami_id}")
        return ami_id

def launch_instance(ec2_client, ec2_resource, ami_id, key_name, sg_id, instance_type="t3.small"):
    print(f"\n[5/6] Launching EC2 instance ({instance_type})...")
    instances = ec2_resource.create_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[sg_id],
        MinCount=1,
        MaxCount=1,
        BlockDeviceMappings=[{
            "DeviceName": "/dev/sda1",
            "Ebs": {
                "VolumeSize": 20,
                "VolumeType": "gp3",
                "DeleteOnTermination": True
            }
        }],
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": "AnyDown-Server"}]
        }]
    )

    try:
        instance = instances[0]
        print(f"      Instance ID: {instance.id}")
        print("      Waiting for instance to reach running state...")
        instance.wait_until_running()
        instance.reload()

        public_ip = instance.public_ip_address
        print(f"      Instance is running! Public IP: {public_ip}")
        return public_ip
    except ClientError as e:
        if "Unsupported" in str(e) and instance_type == "t3.micro":
            print("      t3.micro not supported in this AZ, falling back to t2.micro...")
            return launch_instance(ec2_client, ec2_resource, ami_id, key_name, sg_id, instance_type="t2.micro")
        raise

def wait_for_ssh(public_ip, key_file, max_attempts=30):
    print(f"\n[6/6] Waiting for SSH service to become ready on {public_ip}...")
    ssh_cmd = ["ssh", "-i", str(key_file), "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", f"ubuntu@{public_ip}", "echo ready"]
    
    for attempt in range(1, max_attempts + 1):
        print(f"      Checking SSH connection (attempt {attempt}/{max_attempts})...")
        res = subprocess.run(ssh_cmd, capture_output=True, text=True)
        if res.returncode == 0 and "ready" in res.stdout:
            print("      SSH connection established!")
            return True
        time.sleep(6)
    
    print("\n[ERROR] SSH connection timed out.")
    return False

def package_and_deploy(public_ip, key_file):
    print("\nPackaging and deploying AnyDown stack to EC2...")
    tar_path = PROJECT_ROOT / "anydown-deploy.tar.gz"

    excludes = {
        "node_modules", ".next", "tmp", ".git", ".pytest_cache",
        "anydown-deploy.tar.gz", "shared-hosting-frontend.zip", ".venv"
    }

    def tar_filter(tarinfo):
        parts = Path(tarinfo.name).parts
        if any(part in excludes for part in parts) or tarinfo.name.endswith(".pem"):
            return None
        return tarinfo

    print("      Creating deployment tarball...")
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(PROJECT_ROOT, arcname=".", filter=tar_filter)

    print(f"      Uploading package to ubuntu@{public_ip}...")
    scp_cmd = [
        "scp", "-i", str(key_file),
        "-o", "StrictHostKeyChecking=no",
        str(tar_path), f"ubuntu@{public_ip}:/home/ubuntu/anydown.tar.gz"
    ]
    subprocess.run(scp_cmd, check=True)

    if tar_path.exists():
        tar_path.unlink()

    print("      Unpacking and launching AnyDown containers...")
    remote_script = (
        "mkdir -p /home/ubuntu/anydown && "
        "tar -xzf /home/ubuntu/anydown.tar.gz -C /home/ubuntu/anydown && "
        "rm -f /home/ubuntu/anydown.tar.gz && "
        "cd /home/ubuntu/anydown && "
        "chmod +x setup-ec2.sh && "
        "bash setup-ec2.sh"
    )

    ssh_cmd = [
        "ssh", "-i", str(key_file),
        "-o", "StrictHostKeyChecking=no",
        f"ubuntu@{public_ip}", remote_script
    ]
    subprocess.run(ssh_cmd, check=True)

    print("\n" + "=" * 60)
    print(" DEPLOYMENT COMPLETE! ANYDOWN IS LIVE ON AWS!")
    print("=" * 60)
    print(f" Website URL: http://{public_ip}")
    print(f" API Health:  http://{public_ip}/api/v1/health")
    print(f" SSH Login:   ssh -i \"{key_file}\" ubuntu@{public_ip}")
    print("=" * 60)

def handle_permission_error(e, iam_user="ak"):
    print("\n" + "=" * 60)
    print(" [AWS IAM PERMISSION ERROR]")
    print("=" * 60)
    print(f" Your IAM user '{iam_user}' lacks required EC2 permissions.")
    print(f" Details: {e}\n")
    print(" Quick fix (takes 30 seconds):")
    print(f" 1. Open the AWS IAM Console:")
    print(f"    https://us-east-1.console.aws.amazon.com/iam/home#/users/{iam_user}")
    print(" 2. Click the 'Permissions' tab -> 'Add permissions' -> 'Attach policies directly'")
    print(" 3. Search and check these two policies:")
    print("    • AmazonEC2FullAccess")
    print("    • AmazonSSMReadOnlyAccess")
    print(" 4. Click 'Next' -> 'Add permissions'")
    print(" 5. Re-run: python deploy_aws.py")
    print("=" * 60)
    sys.exit(1)

def main():
    print_header()
    identity = verify_credentials()
    iam_user = identity.get("Arn", "").split("/")[-1] or "ak"
    region = get_region()

    ec2_client = boto3.client("ec2", region_name=region)
    ec2_resource = boto3.resource("ec2", region_name=region)

    try:
        key_file = ensure_key_pair(ec2_client)
        sg_id = ensure_security_group(ec2_client)
        ami_id = get_ubuntu_ami(region)

        instance_type = os.environ.get("ANYDOWN_INSTANCE_TYPE", "t3.micro")
        public_ip = launch_instance(ec2_client, ec2_resource, ami_id, "anydown-ec2-key", sg_id, instance_type)

        if wait_for_ssh(public_ip, key_file):
            package_and_deploy(public_ip, key_file)
    except ClientError as e:
        if "UnauthorizedOperation" in str(e) or "AccessDenied" in str(e):
            handle_permission_error(e, iam_user)
        else:
            raise

if __name__ == "__main__":
    main()

