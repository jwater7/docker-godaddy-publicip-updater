FROM python
LABEL maintainer "j"

RUN pip install requests
RUN pip install pif
RUN pip install godaddypy

COPY godaddy-publicip-updater.py /

CMD [ "python", "/godaddy-publicip-updater.py" ]

