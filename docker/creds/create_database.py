#!/usr/bin/python
"""
Create the database and the user/role, associate it in case,
the database does not exists.
 
"""
import sys
import time

import psycopg2
from pyramid.paster import get_appsettings, setup_logging, _getpathsec
from urllib.parse import urlparse

config_uri = sys.argv[1]

setup_logging(config_uri)
settings = get_appsettings(config_uri)

url = urlparse(settings['aiorm.db.creds'])
if url.scheme not in ('postgresql', 'aiopg+postgresql'):
    raise ValueError('Invalid scheme')

params = {'db': url.path[1:],
          'user': url.username,
          'password': url.password,
          'encoding': 'utf-8',
          }

con = None
try:

    for _ in range(10):
        try:
            con = psycopg2.connect(database='postgres', user='postgres',
                                   host=url.hostname,
                                   port=(url.port or 5432))
        except psycopg2.OperationalError:
            print("Connection failed, retry in 1 second...")
            time.sleep(1)
        else:
            break

    if not con:
        print("Connection failed")
        sys.exit(1)

    con.set_session(autocommit=True)
    cur = con.cursor()

    cur.execute("""SELECT count(*)
                   FROM pg_user
                   WHERE usename = '{user}'
                   """.format(**params))
    exists = cur.fetchone()[0]
    if not exists:
        cur.execute(""" CREATE USER {user} WITH PASSWORD '{password}'
                    """.format(**params))

    cur.execute("""SELECT count(*)
                   FROM pg_database
                   WHERE datname = '{db}'
                   """.format(**params))
    exists = cur.fetchone()[0]
    if not exists:
        cur.execute(""" CREATE DATABASE {db}
                        WITH owner = {user}
                        ENCODING '{encoding}'
                    """.format(**params))
    con.commit()

except psycopg2.DatabaseError as exc:
    import traceback
    print ('Error %s' % exc)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

finally:
    if con:
        con.close()
