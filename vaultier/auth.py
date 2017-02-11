#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Adrián López Tejedor <adrianlzt@gmail.com>
#                  Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

from vaultier.workspacecypher import WorkspaceCypher

from Crypto.Hash import SHA

import binascii
import json
import requests

class Auth(object):
    """Base class for get Vaultier auth token"""
    def __init__(self, server, email, priv_key, pub_key):
        self.server = server
        self.email = email
        self.priv_key = open(priv_key, "r").read()
        self.pub_key = open(pub_key, "r").read()

    def get_token(self):
        """
        Returns user token

        :return: user token string
        :rtype: string
        """
        work_space_cypher = WorkspaceCypher(self.priv_key, self.pub_key)
        server_time = self.fetch_json('/api/server-time').get('datetime')
        sha = SHA.new('{}{}'.format(self.email, server_time).encode('utf-8'))
        signature = binascii.b2a_base64(work_space_cypher.sign(sha))
        data = {'email': self.email, 'date': server_time, 'signature': signature}
        return self.fetch_json('/api/auth/auth', http_method='POST', data=data)['token']

    def fetch_json(self, uri_path, http_method='GET', headers={}, params={}, data=None, files=None, verify=False):
        """Construct the full URL"""
        if uri_path[0] == '/':
            uri_path = uri_path[1:]
            url = '{0}/{1}'.format(self.server, uri_path)

        """Perform the HTTP request"""
        response = requests.request(http_method, url, params=params, headers=headers, data=data, files=files, verify=verify)

        if response.status_code == 401:
            raise Unauthorized('{0} at {1}'.format(response.text, url), response)
        if response.status_code == 403:
            raise Forbidden('{0} at {1}'.format(response.text, url), response)
        if response.status_code not in {200, 206}:
            raise ResourceUnavailable('{0} at {1}'.format(response.text, url), response)

        return response.json()