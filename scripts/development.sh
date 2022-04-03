docker pull redis
docker run --name sexsexder-redis -p 6379:6379 -d redis

docker pull linuxserver/mariadb
docker run -d \
  --name=sexsexder-mariadb \
  -e PUID=1000 \
  -e PGID=1000 \
  -e MYSQL_ROOT_PASSWORD='VEQ~WB{|g^s1' \
  -p 3306:3306 \
  -v /usr/sexsexder/db:/config \
  --restart unless-stopped \
  linuxserver/mariadb