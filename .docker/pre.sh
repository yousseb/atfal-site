# For all servers

apt update && apt dist-upgrade
apt install vim software-properties-common docker.io -y

docker build . -f .docker/Dockerfile-web -tatfal-web
