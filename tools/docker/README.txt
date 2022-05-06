To build the docker image run build.sh or augment this command

$ docker build -t mcc-app .

To run it you will still need your own key, which you provide on the
command line with the --env param:

$ docker run --env CFBD_API_KEY=your_secret_key_here \
    --rm --name running-mcc mcc-app

That will run the default container invocation, which is the current
year in verbose mode. Other options can be sent in directly:

$  docker run --env CFBD_API_KEY=your_secret_key_here \
    --rm --name running-mcc mcc-app \
    python3 /usr/src/app/cfb/vconf/mcc_schedule.py -s 1999 -e 1999

