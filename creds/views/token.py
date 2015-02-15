import asyncio
import logging

import colander
from pyramid.httpexceptions import HTTPBadRequest
from pyramid_aiorest import resource_config, ioschema
from aiorm import orm 

from ..models import Client, RefreshToken
from ..utils import create_token

log = logging.getLogger(__name__)


class PostTokenParams(colander.MappingSchema):
    client_id = colander.SchemaNode(colander.String(), location='json',
                                    )
    client_secret = colander.SchemaNode(colander.String(), location='json',
                                        )
    token_type = colander.SchemaNode(colander.String(), location='json')
    token = colander.SchemaNode(colander.String(), location='json')


class PostTokenReturn(colander.MappingSchema):
    access_token = colander.SchemaNode(colander.String(), location='json')
    refresh_token = colander.SchemaNode(colander.String(), location='json')
    expires_in = colander.SchemaNode(colander.Integer(), location='json')


@resource_config(resource_name='token')
class Token:

    @asyncio.coroutine
    @ioschema(request_schema=PostTokenParams(),
              response_schema=PostTokenReturn())
    def collection_post(self, request):

        meth = '_process_{0}'.format(request.yards['token_type'])
        if not hasattr(self, meth):
            raise HTTPBadRequest(explanation='token_type not implemented')
        return (yield from getattr(self, meth)(request))

    @asyncio.coroutine
    def _process_auth_code(self, request):
        json = request.yards
        authcode = yield from request.cache.get(json['token'])
        if not authcode:
            raise HTTPBadRequest(explanation='Auth code not found')

        if authcode['client_id'] != json['client_id']:
            raise HTTPBadRequest('Auth code not found')
        
        transaction = request.transaction['creds']
        client = yield from Client.by_credentials(transaction,
                                                  json['client_id'],
                                                  json['client_secret'])
        if not client:
            raise HTTPBadRequest(explanation='Client not found')

        access_token = create_token()
        refresh_token = create_token(80)
        yield from request.cache.set(access_token, authcode)
        refresh_token_data = authcode.copy()
        refresh_token_data['access_token'] = access_token

        transaction = request.transaction['creds']
        rtok = RefreshToken(id=refresh_token,
                            client_id=authcode['client_id'],
                            user_id=authcode['user_id'])
        rtok.json = refresh_token_data
        yield from orm.Insert(rtok).run(transaction)

        tokens = {'access_token': access_token,
                  'refresh_token': refresh_token,
                  'expires_in': request.cache.client.ttl}
        return tokens

    @asyncio.coroutine
    def _process_refresh_token(self, request):
        json = request.yards
        transaction = request.transaction['creds']
        old_token = yield from RefreshToken.by_id(transaction, json['token'])
        if not old_token:
            raise HTTPBadRequest(explanation='Token does not exists')

        token_data = old_token.json.copy()

        if token_data['client_id'] != json['client_id']:
            raise HTTPBadRequest('Invalid client')

        client = yield from Client.by_credentials(transaction,
                                                  json['client_id'],
                                                  json['client_secret'])
        if not client:
            raise HTTPBadRequest('Client not found')
        
        
        old_access_token = token_data.pop('access_token')
        log.info('Invalidate access token {}'.format(type(old_access_token)))
        yield from request.cache.pop(old_access_token)
        access_token = create_token()
        refresh_token = create_token(80)

        rtok = RefreshToken(id=refresh_token,
                            client_id=old_token.client_id,
                            user_id=old_token.user_id)
        rtok.json = old_token.json

        yield from orm.Delete(old_token).run(transaction)
        yield from orm.Insert(rtok).run(transaction)

        yield from request.cache.set(access_token, token_data)
        tokens = {'access_token': access_token,
                  'refresh_token': refresh_token,
                  'expires_in': request.cache.client.ttl}
        return tokens
