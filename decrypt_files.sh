#!/bin/bash
# create ams_vault.txt file in main folder

ansible-vault decrypt ams/ams/settings.py --vault-password-file=ams_vault.txt

for i in {dev,prod,stg}; do 
  ansible-vault decrypt ci/jenkins/files/env/$i/docker-compose.yaml --vault-password-file=ams_vault.txt
  ansible-vault decrypt ci/jenkins/files/env/$i/settings.py --vault-password-file=ams_vault.txt
done