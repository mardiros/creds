import sys
import argparse
import asyncio

from pyramid.paster import get_appsettings, setup_logging
from pyramid.config import Configurator
from pyramid.path import DottedNameResolver
from pyramid.settings import aslist


@asyncio.coroutine
def routine(future, callable, config):
    yield from callable(config)
    future.set_result(None)


def main(args=sys.argv):
    if (args[0].endswith('__main__.py')):
        name = args[0].rsplit('/', 2)[-2]
    else:
        name = __name__.split('.', 1)[0]  #setuptools way

    resolver = DottedNameResolver(name)

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='conffile', default='development.ini')
    subparsers = parser.add_subparsers(title='action')

    sp_setup = subparsers.add_parser('setup',
        help='setup {} after the installation'.format(name))
    sp_setup.set_defaults(func='setup')

    kwargs = parser.parse_args(args[1:])
    kwargs = vars(kwargs)

    config_uri = kwargs.pop('conffile')
    func = kwargs.pop('func', None)
    if not func:
        print ('Missing arguments, use --help')
        sys.exit(1)

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, u'main')

    if func != 'setup': # Don't try to configure if it's not setup up
        del settings['pyramid.includes']

    config = Configurator(settings=settings)
    config.end()
    func = resolver.maybe_resolve('{}.bin.{}'.format(name, func))

    loop = asyncio.get_event_loop()
    future = asyncio.Future()
    asyncio.async(routine(future, func, config))
    loop.run_until_complete(future)
    loop.stop()


if __name__ == '__main__':
    main()
