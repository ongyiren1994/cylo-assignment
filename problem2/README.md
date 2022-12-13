# Documentation

## Purpose
The purpose of this tool is to scan over all EC2 instances, and remove the
loose rule (Inbound 0.0.0.0/0 on port 22) from instances which does not have a specific tag.

## Prerequisite
1. A configured AWS profile with sufficient IAM permission

## How to run this tool
1. Create a python3 virtual environment
```
python3 -m venv .venv
```
2. Activate the virtual environment
```
source .venv/bin/activate
```
3. Install the packages
```
pip3 install -r requirements.txt
```
4. Run the program. Replace `Tag Key`,`Tag Name`,`Profile Name`,`Region Name` with the actual values.
```
python3 main.py --tag_key <Tag Key> --tag_value <Tag Value> --profile_name <Profile Name> --region_name <Region Name>
```
