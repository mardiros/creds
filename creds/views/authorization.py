import asyncio

from pyramid.httpexceptions import HTTPOk, HTTPForbidden
from pyramid_aiorest import resource_config


@resource_config(resource_name='authorization')
class Authorization:

    @asyncio.coroutine
    def get(self, request):
        access_token = request.matchdict['access_token']
        http_verb = request.matchdict['http_verb']
        route_url = request.matchdict['route_url']
        data = yield from self.request.cache.get(access_token)
        if not data:
            raise HTTPForbidden('Token expires')
        route = '{0} {1}'.format(http_verb.upper(), route_url)
        return HTTPOk() if route in data['authorization'] else HTTPForbidden()
