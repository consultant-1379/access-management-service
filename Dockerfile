FROM armdocker.rnd.ericsson.se/dockerhub-ericsson-remote/python:3.9-buster


RUN apt-get update && apt-get install nginx libldap2-dev libssl-dev libsasl2-dev vim  nodejs npm -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

RUN mkdir -p /opt/app/ams
RUN mkdir -p /opt/app/ams/log
RUN mkdir -p /opt/app/pip_cache
RUN mkdir -p /opt/app/
COPY requirements.txt start-server.sh /opt/app/
COPY nginx.conf /etc/nginx/nginx.conf
COPY ams /opt/app/ams
COPY certs /opt/app/certs

RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && apt-get install -y nodejs

RUN npm config set @eds:registry https://arm.rnd.ki.sw.ericsson.se/artifactory/api/npm/proj-eds-npm-local \
    && cd /opt/app/ams/static/ && npm install 

RUN  chmod  +x /opt/app/start-server.sh
WORKDIR /opt/app
RUN pip install -r requirements.txt --cache-dir /opt/app/pip_cache
RUN chown -R www-data:www-data /opt/app

EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]
