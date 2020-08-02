# -*- coding: utf-8 -*-
"""
    Copyright (C) 2017 Sebastian Golasch (plugin.video.netflix)
    Copyright (C) 2018 Caphm (original implementation module)
    Copyright (C) 2019 Stefano Gottardo - @CastagnaIT
    Initialize the netflix session

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
from __future__ import absolute_import, division, unicode_literals

import resources.lib.common as common
from resources.lib.database.db_utils import TABLE_SESSION
from resources.lib.globals import g


class SessionBase(object):
    """Initialize the netflix session"""

    session = None
    """The requests.session object to handle communication to Netflix"""

    verify_ssl = True
    """Use SSL verification when performing requests"""

    # Functions from derived classes to allow perform particular operations in parent classes
    external_func_login = None  # (set by access.py)
    external_func_activate_profile = None  # (set by nfsession_op.py)

    def __init__(self):
        self.verify_ssl = bool(g.ADDON.getSettingBool('ssl_verification'))
        self._init_session()

    def _init_session(self):
        """Initialize the session to use for all future connections"""
        try:
            self.session.close()
            common.info('Session closed')
        except AttributeError:
            pass
        from requests import session
        self.session = session()
        self.session.max_redirects = 10  # Too much redirects should means some problem
        self.session.headers.update({
            'User-Agent': common.get_user_agent(enable_android_mediaflag_fix=True),
            'Accept-Encoding': 'gzip, deflate, br'
        })
        common.info('Initialized new session')

    @property
    def account_hash(self):
        """The unique hash of the current account"""
        from base64 import urlsafe_b64encode
        return urlsafe_b64encode(
            common.get_credentials().get('email', 'NoMail').encode('utf-8')).decode('utf-8')

    @property
    def auth_url(self):
        """Access rights to make HTTP requests on an endpoint"""
        return g.LOCAL_DB.get_value('auth_url', table=TABLE_SESSION)

    @auth_url.setter
    def auth_url(self, value):
        g.LOCAL_DB.set_value('auth_url', value, TABLE_SESSION)