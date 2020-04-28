# docker-godaddy-publicip-updater
Periodically update A record at godaddy (DDNS for godaddy domains).  It uses the GoDaddy REST API python library "godaddypy" to update the godaddy IP address to the public IP of the machine that it is running on (via the python library "pif"). By default it checks every 15 minutes, but this can be changed (see below).

## Setup
Go to [GoDaddy developer keys](https://developer.godaddy.com/keys/), log in with your account credentials, and generate a production developer key & secret. Note that the first time wizard creates TEST keys, make sure to also generate a new PRODUCTION API key/secret instead.

## Usage

It uses docker environment variables to control the behavior

### Required Configuration:
| Environment Variable | Value  | Description |
| -------------------- | ------ | ----------- |
| GODADDY_API_KEY      | key    | Use the 'key' from your godaddy account (see the Setup section above) |
| GODADDY_API_SECRET   | secret | Use the 'secret' from your godaddy account (see the Setup section above) |
| GODADDY_DOMAINS      | csv    | A comma-separated list of domains that you'd like to update.  For example: "mydomain.com" or "mydomain.com,anotherdomain.com" |

### Optional Configuration:
| Environment Variable | Value  | Default         | Description |
| -------------------- | ------ | --------------- | ----------- |
| GODADDY_A_NAMES      | csv    | '@'             | A comma-separated list of the 'A' record names you'd like to update.  For example: "home" or "@,anothername" |
| UPDATE_INTERVAL_SEC  | int    | '900' (seconds) | This is the amount of time that the program waits before the public IP is checked for a change and then checks godaddy to check/update the record.  For example: "300" |
| GET_IP_WAIT_SEC      | int    | '10' (seconds)  | This is the amount of time that the program waits before it tries again after a failure to get the host's public IP address.  This is a failsafe for the pif servers and should rarely need to be used. |
| UPDATER_CONFIG_FILE  | string | None            | This is a file path to a JSON formated config file which if it exists would contain a single-level object with default values for the environment variable names given here.  Environment variables specified would override values in the config file.  For example, it may contain: {"GODADDY_A_NAMES": "@,anothername"} |

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
      - "UPDATER_CONFIG_FILE=/config.json"
    volumes:
      - "./config.json:/config.json"
    restart: always
~~~

