# docker-godaddy-publicip-updater
Periodically update A record at godaddy (DDNS for godaddy domains).  It uses the GoDaddy REST API python library "godaddypy" to update the godaddy IP address to the public IP of the machine that it is running on (via the python library "pif"). By default it checks every 15 minutes, but this can be changed (see below).

## Setup
Go to [GoDaddy developer keys](https://developer.godaddy.com/keys/), log in with your account credentials, and generate a production developer key & secret. Note that the first time wizard creates TEST keys, make sure to also generate a new PRODUCTION API key/secret instead.

## Usage

It uses docker environment variables to control the behavior

Required:
~~~
GODADDY_API_KEY=<key>
GODADDY_API_SECRET=<secret>
GODADDY_DOMAINS=mydomain.com
# GODADDY_DOMAINS=mydomain.com,anotherdomain.com
~~~

Optional:
~~~
GODADDY_A_NAMES=@
# GODADDY_A_NAMES=@,anothername
GET_IP_WAIT_SEC=10
UPDATE_INTERVAL_SEC=900
~~~

### Command Line
You can test it out like this:
~~~
sudo docker run --rm \
 -e 'GODADDY_API_KEY=<key>' \
 -e 'GODADDY_API_SECRET=<secret>' \
 -e 'GODADDY_DOMAINS=<mydomain.com>' \
 -it jwater7/godaddy-publicip-updater
~~~

or run it in daemon mode:
~~~
sudo docker run -d --name=godaddy-mydomain-com --restart=always \
 -e 'GODADDY_API_KEY=<key>'
 -e 'GODADDY_API_SECRET=<secret>'
 -e 'GODADDY_DOMAINS=<mydomain.com>'
 jwater7/godaddy-publicip-updater
~~~

### docker-compose
A sample docker-compose:
~~~
  godaddy-mydomain-com:
    image: jwater7/godaddy-publicip-updater
    container_name: godaddy-mydomain-com
    environment:
      - "GODADDY_API_KEY=<key>"
      - "GODADDY_API_SECRET=<secret>"
      - "GODADDY_DOMAINS=mydomain.com"
      - "GODADDY_A_NAMES=@,aname"
      - "GET_IP_WAIT_SEC=30"
      - "UPDATE_INTERVAL_SEC=1800"
    restart: always
~~~

