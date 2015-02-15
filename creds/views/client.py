import asyncio
import logging

import colander
from pyramid.httpexceptions import HTTPNoContent, HTTPNotFound, HTTPBadRequest
from pyramid_aiorest import resource_config, ioschema
from aiorm import orm 

from ..models import Client

log = logging.getLogger(__name__)


class PostClientParams(colander.MappingSchema):
    client_id = colander.SchemaNode(colander.String(), location='json')
    client_secret = colander.SchemaNode(colander.String(), location='json')
    email = colander.SchemaNode(colander.String(), location='json')


class PostClientReturn(colander.MappingSchema):
    location = colander.SchemaNode(colander.String(), location='header')
    status_code = colander.SchemaNode(colander.Integer(),
                                      location='status_code',
                                      default=HTTPNoContent.code)


class GetClientParams(colander.MappingSchema):
    client_id = colander.SchemaNode(colander.String(), location='matchdict')


class GetClientReturn(colander.MappingSchema):
    client_id = colander.SchemaNode(colander.String(), location='json')
    email = colander.SchemaNode(colander.String(), location='json')
    status = colander.SchemaNode(colander.String(), location='json')


@resource_config(resource_name='client')
class ClientResource:

    @asyncio.coroutine
    @ioschema(request_schema=PostClientParams(),
              response_schema=PostClientReturn())
    def collection_post(self, request):
        params = request.yards

        client = yield from Client.by_id(request.transaction['creds'],
                                           request.yards['client_id'])
        if client:
            raise HTTPBadRequest(explanation='Duplicate client_id')

        client = Client(id=params['client_id'], email=params['email'])
        client.client_secret = params['client_secret']
        yield from orm.Insert(client).run(request.transaction['creds'])
        log.info('Client {client_id} created'
                 ''.format(client_id=client.id))
        return {'location': request.route_path('resource_client',
                                               client_id=client.id)}

    @asyncio.coroutine
    @ioschema(request_schema=GetClientParams(),
              response_schema=GetClientReturn())
    def get(self, request):
        client = yield from Client.by_id(request.transaction['creds'],
                                           request.yards['client_id'])
        if not client:
            raise HTTPNotFound()
        json = client.to_dict()
        json['client_id'] = json['id']
        return json

