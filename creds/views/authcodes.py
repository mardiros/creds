import asyncio
import logging

import colander
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest
from pyramid_aiorest import resource_config, ioschema

from ..models import Client
from ..utils import create_token


log = logging.getLogger(__name__)


class PostAuthCodeParams(colander.MappingSchema):
    authentication_token = colander.SchemaNode(colander.String(),
                                               location='json',
                                               )
    client_id = colander.SchemaNode(colander.String(), location='json')

    @colander.instantiate(name='scope', location='json')
    class Scope(colander.SequenceSchema):
        @colander.instantiate()
        class ScopeItem(colander.MappingSchema):

            route_url = colander.SchemaNode(colander.String())

            @colander.instantiate(name='http_verbs', missing=colander.drop)
            class HTTPVerbs(colander.SequenceSchema):
                schema = colander.SchemaNode(colander.String(),
                                             )


class AuthCodeReturn(colander.MappingSchema):
    authorization_code = colander.SchemaNode(colander.String(),
                                             location='json',
                                             )


@resource_config(resource_name='authcode')
class AuthCode:

    @asyncio.coroutine
    @ioschema(request_schema=PostAuthCodeParams(),
              response_schema=AuthCodeReturn())
    def collection_post(self, request):

        transaction = request.transaction['creds']
        user = yield from request.cache.get(
            request.yards['authentication_token'])

        if not user:
            raise HTTPBadRequest('Session expired')

        client_id = request.yards['client_id']
        client = Client.by_id(transaction, client_id)
        if not client:
            yield from request.cache.delete(
                request.yards['authentication_token'])
            raise HTTPBadRequest('Client not found')
        
        token = create_token()
        authorization = set()

        for item in request.yards.get('scope', []):
            route_url = item['route_url']
            verbs = item.get('http_verbs',
                             ['GET', 'HEAD', 'OPTIONS', 'POST', 'PATCH', 'PUT',
                              'DELETE'])
            for verb in verbs:
                route = '{0} {1}'.format(verb.upper(), route_url)
                authorization.add(route)

        log.info('Creating auth code for user: {username} / client: '
                 '{client_id}'.format(username=user['username'],
                                      client_id=client_id))
        yield from request.cache.set(
            token,
            {'user_id': user['user_id'],
             'username': user['username'],
             'client_id': client_id,
             'authorization': list(authorization)
             })
        return {'authorization_code': token}
