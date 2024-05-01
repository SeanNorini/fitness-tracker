#!/bin/sh

echo DEBUG=0 >> .env
echo SQL_ENGINE=django.db.backends.postgresql >> .env
echo DATABASE=postgres >> .env

echo SECRET_KEY=$SECRET_KEY >> .env
echo SQL_DATABASE=$SQL_DATABASE >> .env
echo SQL_USER=$SQL_USER >> .env
echo SQL_PASSWORD=$SQL_PASSWORD >> .env
echo SQL_HOST=$SQL_HOST >> .env
echo SQL_PORT=$SQL_PORT >> .env
echo WEB_IMAGE=$IMAGE:web  >> .env
echo NGINX_IMAGE=$IMAGE:nginx-proxy  >> .env
echo CI_REGISTRY_USER=$CI_REGISTRY_USER   >> .env
echo CI_JOB_TOKEN=$CI_JOB_TOKEN  >> .env
echo CI_REGISTRY=$CI_REGISTRY  >> .env
echo IMAGE=$CI_REGISTRY/$(echo $CI_PROJECT_NAMESPACE | tr '[:upper:]' '[:lower:]')/$(echo $CI_PROJECT_NAME | tr '[:upper:]' '[:lower:]') >> .env
echo APP_ID=$APP_ID >> .env
echo APP_KEY=$APP_KEY >> .env
echo EMAIL_BACKEND=$EMAIL_BACKEND >> .env
echo EMAIL_HOST=$EMAIL_HOST >> .env
echo EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD >> .env
echo EMAIL_HOST_USER=$EMAIL_HOST_USER >> .env
echo VIRTUAL_HOST=$VIRTUAL_HOST >> .env
echo VIRTUAL_PORT=$VIRTUAL_PORT >> .env
echo CSRF_TRUSTED_ORIGINS=$CSRF_TRUSTED_ORIGINS >> .env
echo LETSENCRYPT_HOST=$LETSENCRYPT_HOST >> .env
echo ACME_CA_URI=$ACME_CA_URI >> .env
echo NGINX_PROXY_CONTAINER=$NGINX_PROXY_CONTAINER >> .env