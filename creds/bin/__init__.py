import asyncio
import logging
import os
import sys

from aiorm import orm
from pyramid_aiorm import includeme
from creds import models

log = logging.getLogger(__name__)

@asyncio.coroutine
def get_group(transaction, group_name):
    group = yield from models.Group.by_name(transaction, group_name)
    if not group:
        group = models.Group(name=group_name)
        yield from orm.Insert(group).run(transaction)
    return group


@asyncio.coroutine
def setup(config):
    log.info('Setup application')
    log.info('Connecting to the database')

    yield from includeme(config)

    # with (yield from orm.transaction('creds')) as trans:

    trans = orm.Transaction('creds')
    try:

        log.info('Creating the database schema')
        yield from orm.CreateSchema('creds').run(trans)
        yield from trans.commit()
    except Exception:
        log.exception('Unexpected exception')
        yield from trans.rollback()
