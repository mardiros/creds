creds
=====

An API to create an OAuth2 mechanism.


Installation
------------

Currently, its in development, but you can run it in a Docker container using
fig.


::

  $ git clone https://github.com/mardiros/creds.git
  $ cd creds
  $ fig run wsgi


Usage
-----

::

  >>> import requests, json
  >>> jsonhdr = {'Content-Type': 'application/json'}
  >>> # Create a user
  >>> bob = {'username': 'marley', 'password': 'positivevibration', 'email': 'bob@bobmarley.com'}
  >>> requests.post('http://localhost:6543/users', data=json.dumps(bob), headers=jsonhdr).headers['location']
  'http://localhost:6543/users/marley'
  >>> requests.get(_).json()
  {'username': 'marley', 'status': 'active', 'email': 'bob@bobmarley.com'}
  >>>
  >>> # Create a client
  >>> tuffgong = {'client_id': 'tuffgong', 'client_secret': 'reggaemusic', 'email': 'contact@tuffgong.com'}
  >>> requests.post('http://localhost:6543/clients', data=json.dumps(tuffgong), headers=jsonhdr).headers['location']
  >>> requests.get(_).json()
  {'client_id': 'tuffgong', 'status': 'active', 'email': 'contact@tuffgong.com'}
  >>>
  >>> # Create an authentication token to keep in the OAuth2 authorization server session,
  >>> # user stay logged in for creating many authorization for many clients.
  >>> requests.post('http://localhost:6543/authentication', data=json.dumps({'username': 'marley', 'password': 'positivevibration'}), headers=jsonhdr).json()
  {'authentication_token': 'fc018cc93f36024f060384d9ab644e463f3b79cd'}

  >>> # Create an the authentication token in the OAuth2 authorization server session, and pass it to the client via the user's browser
  >>> requests.post('http://localhost:6543/authcodes', data=json.dumps({'authentication_token': _['authentication_token'], 'client_id': 'tuffgong', 'scope': [{'route_url': '/a/resource'}]}), headers={'Content-Type': 'application/json'}).json()
  {'authorization_code': '795989226e1a8303660c67d9247cef35e3e15935'}

  >>> # Create an the access/refresh token in the client application
  >>> requests.post('http://localhost:6543/tokens', data=json.dumps({'token': _['authorization_code'], 'client_id': 'tuffgong', 'client_secret': 'reggaemusic', 'token_type': 'auth_code'}), headers={'Content-Type': 'application/json'}).json()
  {'access_token': 'f061d3d5e7fea50c3e26dc148f659d66e3bff15c',
   'refresh_token': '3b2e335e49127a5be19025e502c8dd8d610081930726d5a3d5df1186e0675746941d2dcc188cfb35',
   'expires_in': 3600}
  >>> # Refresh the token in the client application
  >>> requests.post('http://localhost:6543/tokens', data=json.dumps({'token': _['refresh_token'], 'client_id': 'tuffgong', 'client_secret': 'reggaemusic', 'token_type': 'refresh_token'}), headers={'Content-Type': 'application/json'}).json()
  {'access_token': '571eeb70fbfcef6f74a868cd380286ea7484ceb9',
   'refresh_token': 'f973e1ca34b7280befcd8851a1be0ca7a4aa58fc075f3f74f7d703a4d14225a9e7c375f165fe9d3e',
   'expires_in': 3600}
  >>> # And again
  >>> requests.post('http://localhost:6543/tokens', data=json.dumps({'token': _['refresh_token'], 'client_id': 'tuffgong', 'client_secret': 'reggaemusic', 'token_type': 'refresh_token'}), headers={'Content-Type': 'application/json'}).json()
  {'access_token': '3781a41ec4033cdc8d565bef4ee0e4224b3c1fcc',
   'refresh_token': 'e3c1342195988783a43b191a3b3c2fd617963512c4f2ea838c94c5f010047d3951aaac26076dd993',
   'expires_in': 3600}
