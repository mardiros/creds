import asyncio
import logging

import colander
from pyramid.httpexceptions import HTTPNoContent, HTTPNotFound, HTTPBadRequest
from pyramid_aiorest import resource_config, ioschema
from aiorm import orm 

from ..models import User, UserGroup

log = logging.getLogger(__name__)


class PostUserParams(colander.MappingSchema):
    username = colander.SchemaNode(colander.String(), location='json')
    email = colander.SchemaNode(colander.String(), location='json')
    password = colander.SchemaNode(colander.String(), location='json')


class PostUserReturn(colander.MappingSchema):
    location = colander.SchemaNode(colander.String(), location='header')
    status_code = colander.SchemaNode(colander.Integer(),
                                      location='status_code',
                                      default=HTTPNoContent.code)


class GetUserParams(colander.MappingSchema):
    username = colander.SchemaNode(colander.String(), location='matchdict')


class GetUserReturn(colander.MappingSchema):
    username = colander.SchemaNode(colander.String(), location='json')
    email = colander.SchemaNode(colander.String(), location='json')
    status = colander.SchemaNode(colander.String(), location='json')


@resource_config(resource_name='user')
class UserResource:

    @asyncio.coroutine
    @ioschema(request_schema=PostUserParams(),
              response_schema=PostUserReturn())
    def collection_post(self, request):
        params = request.yards

        user = yield from User.by_username(request.transaction['creds'],
                                           request.yards['username'])
        if user:
            raise HTTPBadRequest(explanation='Duplicate username')

        user = User(username=params['username'], email=params['email'])
        user.password = params['password']
        yield from orm.Insert(user).run(request.transaction['creds'])
        log.info('User {username} created with id {user_id}'
                 ''.format(username=user.username,
                           user_id=user.id))
        return {'location': request.route_path('resource_user',
                                               username=user.username)}

    @asyncio.coroutine
    @ioschema(request_schema=GetUserParams(),
              response_schema=GetUserReturn())
    def get(self, request):
        user = yield from User.by_username(request.transaction['creds'],
                                           request.yards['username'])
        if not user:
            raise HTTPNotFound()
        return user.to_dict()
