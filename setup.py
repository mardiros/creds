import os
import sys

from setuptools import setup, find_packages

py_version = sys.version_info[:2]
if py_version < (3, 3):
    raise Exception("websockets requires Python >= 3.3.")


here = os.path.abspath(os.path.dirname(__file__))
NAME = 'creds'
with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()
with open(os.path.join(here, 'CHANGES.rst')) as changes:
    CHANGES = changes.read()

requires = [
    'pyramid',
    'gunicorn',
    'aiohttp',
    'pyramid_jinja2',
    'asyncio_redis',
    'pyramid-kvs',
    'psycopg2',
    'simplejson',
    'pyramid_yards',
    'pyramid_asyncio',
    'cryptacular',
    ]

setup(name=NAME,
      version='0.0',
      description='A Credentials API',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Guillaume Gauvrit',
      author_email='guillaume@gauvr.it',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite=''.format('{}.tests'.format(NAME)),
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      {name} = {name}.__main__:main

      [paste.app_factory]
      main = {name}:main
      """.format(name=NAME),
      )
