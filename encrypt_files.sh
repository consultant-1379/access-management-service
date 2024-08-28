#!/bin/bash
# create ams_vault.txt file in main folder 

ansible-vault encrypt ams/ams/settings.py --vault-password-file=ams_vault.txt

for i in {dev,prod,stg}; do
  ansible-vault encrypt ci/jenkins/files/env/$i/docker-compose.yaml --vault-password-file=ams_vault.txt
  ansible-vault encrypt ci/jenkins/files/env/$i/settings.py --vault-password-file=ams_vault.txt
done