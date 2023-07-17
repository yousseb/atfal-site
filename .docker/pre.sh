# For all servers

apt update && apt dist-upgrade
apt install vim software-properties-common docker.io -y

sudo chmod +x /usr/local/bin/docker-compose

sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

docker build . -f .docker/Dockerfile-web -tatfal-web
