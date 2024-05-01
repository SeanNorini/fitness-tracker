#!/bin/sh

ssh -o StrictHostKeyChecking=no ubuntu@$EC2_PUBLIC_IP_ADDRESS << 'ENDSSH'
  cd /home/ubuntu/app
  export $(cat .env | xargs)
  docker login -u $CI_REGISTRY_USER -p $CI_JOB_TOKEN $CI_REGISTRY
  docker pull $IMAGE:web
  docker pull $IMAGE:nginx-proxy
  docker-compose -f docker-compose.prod.yml up -d
ENDSSH