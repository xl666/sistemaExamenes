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

RUN mkdir /code
RUN mkdir /start

COPY ./run.sh /start
RUN chmod 751 /start/run.sh

WORKDIR /code

RUN useradd -s /bin/bash limitado

RUN chown -R limitado /code

CMD /start/run.sh