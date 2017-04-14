#!/bin/bash

cd ~  
git clone https://github.com/appsembler/configuration 
cd configuration 
git checkout appsembler/eucalyptus/master 
pip install -r requirements.txt 
cd playbooks  

#link edx_ansible roles and libraries
ln -s ~/configuration/playbooks/roles ~/edx-theme/deploy/roles
ln -s ~/configuration/playbooks/library ~/edx-theme/deploy/library

#deploy
ansible-playbook -i ~/inventory --user $CIRCLE_USER ~/edx-theme/deploy/aquent_deploy.yml

