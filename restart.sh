docker stop mh-rcon-persistent-titles
docker rm mh-rcon-persistent-titles
docker build . -t mh-rcon-persistent-titles-img
docker run -d -v ./persist/:/bot/persist/ --rm --name mh-rcon-persistent-titles mh-rcon-persistent-titles-img
