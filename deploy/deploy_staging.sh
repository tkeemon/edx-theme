#!/bin/bash

cd ~  
git clone https://github.com/appsembler/configuration 
cd configuration 
git checkout appsembler/eucalyptus/master 
pip install -r requirements.txt 
cd playbooks  

ansible-playbook -i ~/inventory --user $CIRCLE_USER ~/deploy/aquent_deploy.yml

