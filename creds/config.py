
def includeme(config):

    # OAuth2 authorization server helpers

    # Build a user session in an OAuth authorization server
    config.add_resource_route('authentication', '/authentication',
                              '/authentication/{token}')

    config.add_resource_route('authcode', '/authcodes')
    config.add_resource_route('token', '/tokens')

    # Oauth2 resource server helpers
    config.add_resource_route('authorization',
                              path='/authorization/'
                                   '{access_token}/{http_verb}/*route_url')

    # Management of resources
    config.add_resource_route('user', '/users', '/users/{username}')
    config.add_resource_route('client', '/clients', '/clients/{client_id}')

    config.scan('creds.views')
