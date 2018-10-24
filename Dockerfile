FROM centos:latest
LABEL maintainer="bus-txn Team <gobus@go-mmt.com>"

ARG DEPOT_BUILD_ENV

RUN mkdir -p /logs /logs/newrelic /etc/newrelic /logs/celery_logs/ /var/log/nginx /var/log/supervisor /etc/supervisord.d && \
    touch /logs/depot_uwsgi.log && \
    touch /logs/depot_apps.log && \
    touch /logs/newrelic/newrelic_depot.log && \
    touch /etc/newrelic/newrelic-depot.ini && \
    touch /logs/uwsgi-touch-logrotate.txt && touch /logs/uwsgi-reload.txt && \
    chmod 0777 -R /logs/ && \
    yum -y install \
              epel-release \
              python-setuptools \
              python-pip \
              geoip geoip-devel \
              snappy-devel \
              mysql-devel \
              expat-devel \
              wget \
              make \
              gcc-c++ \
              libffi-devel \
              zlib-devel \
              python-devel \
              sqlite-devel \
              libcurl-devel \
              && yum clean all

RUN yum install -y nginx && \
    easy_install supervisor && \
    rm -f /etc/localtime && \
    ln -s /usr/share/zoneinfo/Asia/Kolkata /etc/localtime

# Install python3.6.4
RUN cd /opt && \
  wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz && \
  tar xvf Python-3.6.4.tgz && \
  cd /opt/Python-3.6.4 && \
  ./configure --enable-shared --with-system-ffi --with-system-expat --enable-loadable-sqlite-extensions --prefix=/usr/local/python3 LDFLAGS="-L/usr/local/python3/extlib/lib -Wl,--rpath=/usr/local/python3/lib -Wl,--rpath=/usr/local/python3/extlib/lib" CPPFLAGS="-I/usr/local/python3/extlib/include" && \
  make && \
  make altinstall

# Install Protobuff
RUN \
  cd /opt && \
  wget https://github.com/goibibo/protoc/blob/master/protobuf-3.5.1-1.x86_64.rpm?raw=true -O protobuf-3.5.1-1.x86_64.rpm && \
  rpm -i protobuf-3.5.1-1.x86_64.rpm && \
  ldconfig
#  ldconfig && \
#  wget https://github.com/google/protobuf/releases/download/v3.5.1/protobuf-python-3.5.1.tar.gz && \
#  tar -xvzf protobuf-python-3.5.1.tar.gz && \
#  cd protobuf-3.5.1/python/ && \
#  /usr/local/python3/bin/python3.6 setup.py install --cpp_implementation && \
#  rm -rf /srv/VENVs/depot/lib/python3.6/site-packages/google/protobuf && \
#  cp -r /usr/local/python3/lib/python3.6/site-packages/protobuf-3.5.1-py3.6-linux-x86_64.egg/google/protobuf/ /usr/local/python3/lib/python3.6/site-packages/google/


WORKDIR /usr/local/goibibo/depot

EXPOSE 80

RUN pwd

COPY ./ /usr/local/goibibo/depot


RUN ls

RUN pwd

COPY config/docker/supervisord.conf /etc/supervisord.conf
COPY config/docker/supervisord /etc/rc.d/init.d/supervisord
COPY config/docker/services/depot_services.conf /etc/supervisord.d/services.conf
COPY config/docker/etc/nginx.conf /etc/nginx/nginx.conf
COPY config/docker/${DEPOT_BUILD_ENV}/newrelic_depot.ini /etc/newrelic/newrelic_depot.ini
COPY config/docker/${DEPOT_BUILD_ENV}/depot.conf /etc/nginx/conf.d/depot.conf
COPY config/docker/${DEPOT_BUILD_ENV}/uwsgi-depot.ini /etc/uwsgi-depot.ini

#COPY ./ /usr/local/goibibo/depot

COPY config/docker/wsgi.py /usr/local/goibibo/depot/depot/depot_proj/wsgi.py

RUN \
    /usr/local/python3/bin/pip3.6 install --upgrade pip && \
    if [ "$DEPOT_BUILD_ENV" == "dev" ]; then /usr/local/python3/bin/pip3.6 install -r config/pip/requirements_dev.txt; else /usr/local/python3/bin/pip3.6 install -r config/pip/requirements.txt; fi && \
    /usr/local/python3/bin/pip3.6 install -r config/pip/requirement_options.txt && \
    /usr/local/python3/bin/python3.6 /usr/local/goibibo/depot/depot/manage.py collectstatic && \
    chmod 755 /etc/rc.d/init.d/supervisord

CMD ["/usr/bin/supervisord", "-n"]
