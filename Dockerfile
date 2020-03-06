from ubuntu:latest

ARG slack_api_token
ARG slack_sign_secret
ARG daudit_internal_pass

ENV SLACK_API_TOKEN=$slack_api_token
ENV SLACK_SIGNING_SECRET=$slack_sign_secret
ENV DAUDIT_INTERNAL_PASS=$daudit_internal_pass

RUN apt-get update \
    && apt-get install -y sudo \
    && sudo apt-get install -y python3-pip \
    && sudo apt-get install -y mysql-server

COPY docker-entrypoint.sh /usr/local/bin
RUN ln -s /usr/local/bin/docker-entrypoint.sh / # backwards compatible
RUN chmod +x docker-entrypoint.sh

COPY /application /home/application
RUN chmod +x /home/application
WORKDIR /home/application
RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 3000
ENTRYPOINT ["docker-entrypoint.sh"]
CMD python3 app.py
