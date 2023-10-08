FROM python:3.8

RUN mkdir /dependencias

COPY requeriments.txt /dependencias

RUN pip3 install -r /dependencias/requeriments.txt

ENV SECRET_KEY_ESCRITO=""
ENV DB_USER_ESCRITO=""
ENV DB_NAME_ESCRITO=""
ENV DB_PASSWORD_ESCRITO=""
ENV DB_HOST_ESCRITO=""
ENV DB_PORT_ESCRITO=3306
ENV PATH_PREFIX=""
ENV BOT_TOKEN=""
ENV BOT_CHATID=""

RUN mkdir /code
RUN mkdir /start
RUN mkdir /monitor

COPY ./run.sh /start
RUN chmod 751 /start/run.sh
COPY ./monitor.py /monitor

WORKDIR /code

RUN useradd -s /bin/bash limitado

RUN chown -R limitado /code
RUN chown -R limitado /start

USER limitado

CMD /start/run.sh
