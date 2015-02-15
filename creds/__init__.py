from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('creds.config',
                   route_prefix=settings.get('creds.route_prefix'))
    return config.make_asyncio_app()
