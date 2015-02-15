import asyncio
import logging

import colander
from pyramid import httpexceptions
from pyramid_aiorest import resource_config, ioschema

from ..models import User
from ..utils import create_token


log = logging.getLogger(__name__)


class PostAuthenticationParams(colander.MappingSchema):
    username = colander.SchemaNode(colander.String(), location='json')
    password = colander.SchemaNode(colander.String(), location='json')


class PostAuthenticationReturn(colander.MappingSchema):
    authentication_token = colander.SchemaNode(colander.String(),
                                               location='json',
                                               )


class GetAuthenticationParams(colander.MappingSchema):
    token = colander.SchemaNode(colander.String(), location='matchdict')


class GetAuthenticationReturn(colander.MappingSchema):
    username = colander.SchemaNode(colander.String(), location='json')


@resource_config(resource_name='authentication')
class Authentication:

    @asyncio.coroutine
    @ioschema(request_schema=PostAuthenticationParams(),
              response_schema=PostAuthenticationReturn())
    def collection_post(self, request):
        transaction = request.transaction['creds']
        user = yield from User.by_credentials(transaction,
                                              request.yards['username'],
                                              request.yards['password'])

        if not user:
            raise httpexceptions.HTTPBadRequest(explanation='Bad username or '
                                                            'password')
        token = create_token()
        yield from request.cache.set(token,
                                     {'user_id': user.id,
                                      'username': user.username,
                                      })
        log.info('Create an authentication token for {username}'
                 ''.format(username=user.username))
        return {'authentication_token': token}

    @asyncio.coroutine
    @ioschema(request_schema=GetAuthenticationParams(),
              response_schema=PostAuthenticationReturn())
    def get(self, request):
        username = yield from request.cache.get(request.yards['token'])
        if not username:
            raise httpexceptions.HTTPNotFound()
        transaction = request.transaction['creds']
        user = yield from User.by_username(transaction, username)
        if not user:
            raise httpexceptions.HTTPGone()
        return user.as_dict()
    