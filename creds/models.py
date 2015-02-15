import asyncio
import logging

import simplejson as json
import cryptacular.bcrypt
from aiorm import orm

log = logging.getLogger(__name__)
bcrypt = cryptacular.bcrypt.BCRYPTPasswordManager()


class ModelError(Exception):
    """ A base Exception for models validation """

class Table:
    """
    A class that initialize column from the given kwargs
    """
    def __init__(self, **kwargs):

        for key, val in kwargs.items():
            if not hasattr(self.__class__, key):
                raise RuntimeError('Field {} not declared'.format(key))
            setattr(self, key, val)

    def __repr__(self):
        return '<Table {} #{}>'.format(self.__class__.__name__, self.id)

    def to_dict(self):
        return {col: getattr(self, col) for col in self.__meta__['columns']}

    @property
    def collection(self):
        return self.__meta__['tablename']

    @asyncio.coroutine
    def validate(self):
        return True

    @classmethod
    @asyncio.coroutine
    def by_id(cls, transaction, id):
        return (yield from orm.Get(cls, id).run(transaction))

    @classmethod
    @asyncio.coroutine
    def all(cls, transaction):
        return (yield from (orm.Select(cls).run(transaction, fetchall=True)))


@orm.table(database='creds', name='user_group')
class UserGroup(Table):
    group_id = orm.ForeignKey('group.id', primary_key=True)
    user_id = orm.ForeignKey('user.id', primary_key=True)


@orm.table(database='creds', name='group')
class Group(Table):

    id = orm.PrimaryKey(orm.Integer, autoincrement=True)
    created_at = orm.Column(orm.Timestamp, default=orm.utc_now())
    name = orm.Column(orm.String, length=255, unique=True)
    users = orm.ManyToMany('user', 'user_group')

    @classmethod
    @asyncio.coroutine
    def by_name(cls, transaction, name):
        return (yield from (orm.Select(cls).where(cls.name == name)
                                           .run(transaction,
                                                fetchall=False)))


@orm.table(database='creds', name='user')
class User(Table):

    id = orm.PrimaryKey(orm.Integer, autoincrement=True)
    created_at = orm.Column(orm.Timestamp, default=orm.utc_now())
    username = orm.Column(orm.String, length=24, unique=True)
    _password = orm.Column('password', orm.String, length=60)
    # 'active', 'deleted'
    status = orm.Column(orm.String, length=20, default='active')
    email = orm.Column(orm.String, length=255, unique=True)
    groups = orm.ManyToMany('group', 'user_group')

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, clear_password):
        self._password = bcrypt.encode(clear_password, rounds=12)

    @classmethod
    @asyncio.coroutine
    def by_username(cls, transaction, username):
        return (yield from (orm.Select(cls).where(cls.username == username,
                                                  cls.status == 'active')
                                           .run(transaction,
                                                fetchall=False)))

    @classmethod
    @asyncio.coroutine
    def by_credentials(cls, transaction, username, password):
        user = yield from cls.by_username(transaction, username)
        if not user:
            return None
        return user if bcrypt.check(user.password, password) else None


@orm.table(database='creds', name='client')
class Client(Table):
    id = orm.PrimaryKey(orm.String, length=24, unique=True)
    email = orm.Column(orm.String, length=255, unique=True)
    created_at = orm.Column(orm.Timestamp, default=orm.utc_now())
    _client_secret = orm.Column('client_secret', orm.String, length=64)
    # 'active', 'deleted'
    status = orm.Column(orm.String, length=20, default='active')

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, clear_client_secret):
        self._client_secret = bcrypt.encode(clear_client_secret, rounds=12)

    @classmethod
    @asyncio.coroutine
    def by_id(cls, transaction, id):
        return (yield from (orm.Select(cls).where(cls.id == id,
                                                  cls.status == 'active')
                                           .run(transaction,
                                                fetchall=False)))

    @classmethod
    @asyncio.coroutine
    def by_credentials(cls, transaction, client_id, client_secret):
        client = yield from cls.all(transaction)
        log.info('clients')
        for c in client:
            log.info(c.id)
        client = yield from cls.by_id(transaction, client_id)
        log.info('client')
        log.info(client)
        if not client:
            return None
        log.info(client.client_secret)
        log.info(client_secret)
        return client if bcrypt.check(client.client_secret,
                                      client_secret) else None


@orm.table(database='creds', name='refresh_token')
class RefreshToken(Table):

    # a client can have only one refresh token per user at the time
    id = orm.Column(orm.String, length=80, primary_key=True)
    client_id = orm.ForeignKey('client.id')
    user_id = orm.ForeignKey('user.id')
    _json = orm.Column('json', orm.Text)
    _json_decoded = None

    @property
    def json(self):
        if self._json_decoded is None:
            self._json_decoded = json.loads(self._json)
        return self._json_decoded

    @json.setter
    def json(self, toencode):
        self._json = json.dumps(toencode)
        self._json_decoded = toencode
