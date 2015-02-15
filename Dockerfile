from python:3.4

# This image is intend to be used to test/develop
# pyshop in docker containers for mysql and postgresql
MAINTAINER Guillaume Gauvrit <guillaume@gauvr.it>

EXPOSE 6543

RUN apt-get update
RUN apt-get install -y python-dev libpq-dev python-pip git
RUN pip install -U pip

RUN pip install git+https://github.com/mardiros/pyramid_yards.git
RUN pip install git+https://github.com/Gandi/pyramid_kvs.git
RUN pip install git+https://github.com/mardiros/pyramid_asyncio.git
RUN pip install git+https://github.com/mardiros/aiorm.git
RUN pip install git+https://github.com/mardiros/pyramid_aiorm.git
RUN pip install git+https://github.com/mardiros/pyramid_aiorest.git


RUN useradd -m docker

ADD . /srv/creds
WORKDIR /srv/creds

RUN python setup.py install
RUN python setup.py develop
RUN chown -R docker /srv/creds
RUN cp /srv/creds/docker/creds/entrypoint.sh /docker-entrypoint.sh
RUN chmod 750 /docker-entrypoint.sh
RUN chown docker /docker-entrypoint.sh


USER docker
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["pserve", "development.ini"]
