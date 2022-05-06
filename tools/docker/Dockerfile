FROM python:3

WORKDIR /usr/src/app

RUN pip install cfbd
RUN git clone https://github.com/mcccfb/cfb.git

WORKDIR cfb/vconf

CMD [ "python3", "./mcc_schedule.py", "-v" ]
