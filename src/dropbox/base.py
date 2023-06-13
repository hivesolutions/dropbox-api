#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Dropbox API
# Copyright (c) 2008-2020 Hive Solutions Lda.
#
# This file is part of Hive Dropbox API.
#
# Hive Dropbox API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Dropbox API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Dropbox API. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2020 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

from . import file
from . import user
from . import shared_link

BASE_URL = "https://api.dropboxapi.com/2/"
""" The default base URL to be used when no other
base URL value is provided to the constructor """

CONTENT_URL = "https://content.dropboxapi.com/2/"
""" The default content URL to be used when no other
content URL value is provided to the constructor """

WEB_URL = "https://www.dropbox.com/"
""" The default web URL to be used when no other
web URL value is provided to the constructor """

API_URL = "https://api.dropboxapi.com/"
""" The default api URL to be used when no other
api URL value is provided to the constructor """

CLIENT_ID = None
""" The default value to be used for the client id
in case no client id is provided to the API client """

CLIENT_SECRET = None
""" The secret value to be used for situations where
no client secret has been provided to the client """

REDIRECT_URL = "http://localhost:8080/oauth"
""" The redirect URL used as default (fallback) value
in case none is provided to the API (client) """

SCOPE = ()
""" The list of permissions to be used to create the
scope string for the OAuth value """

ACCESS_TOKEN = None
""" The default access token to be applied to the
client when no other is provided """

REFRESH_TOKEN = None
""" The default refresh token to be applied to the
client when no other is provided """

class API(
    appier.OAuth2API,
    file.FileAPI,
    user.UserAPI,
    shared_link.SharedLinkAPI
):

    def __init__(self, *args, **kwargs):
        appier.OAuth2API.__init__(self, *args, **kwargs)
        self.client_id = appier.conf("DROPBOX_KEY", CLIENT_ID)
        self.client_id = appier.conf("DROPBOX_ID", self.client_id)
        self.client_secret = appier.conf("DROPBOX_SECRET", CLIENT_SECRET)
        self.redirect_url = appier.conf("DROPBOX_REDIRECT_URL", REDIRECT_URL)
        self.access_token = appier.conf("DROPBOX_TOKEN", ACCESS_TOKEN)
        self.refresh_token = appier.conf("DROPBOX_REFRESH", REFRESH_TOKEN)
        self.base_url = kwargs.get("base_url", BASE_URL)
        self.content_url = kwargs.get("content_url", CONTENT_URL)
        self.web_url = kwargs.get("web_url", WEB_URL)
        self.api_url = kwargs.get("api_url", API_URL)
        self.client_id = kwargs.get("client_id", self.client_id)
        self.client_secret = kwargs.get("client_secret", self.client_secret)
        self.redirect_url = kwargs.get("redirect_url", self.redirect_url)
        self.scope = kwargs.get("scope", SCOPE)
        self.access_token = kwargs.get("access_token", self.access_token)
        self.refresh_token = kwargs.get("refresh_token", self.refresh_token)

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        appier.OAuth2API.build(
            self,
            method,
            url,
            data = data,
            data_j = data_j,
            data_m = data_m,
            headers = headers,
            params = params,
            mime = mime,
            kwargs = kwargs
        )
        if not self.is_oauth(): return
        kwargs.pop("access_token", True)

    def auth_callback(self, params, headers):
        if not self.refresh_token: return
        self.oauth_refresh()
        params["access_token"] = self.get_access_token()
        headers["Authorization"] = "Bearer %s" % self.get_access_token()

    def oauth_authorize(self, state = None, token_access_type = "offline", prompt = True):
        url = self.web_url + "oauth2/authorize"
        values = dict(
            client_id = self.client_id,
            redirect_uri = self.redirect_url,
            response_type = "code",
            scope = " ".join(self.scope)
        )
        if state: values["state"] = state
        if token_access_type: values["token_access_type"] = token_access_type
        if not prompt: values["prompt"] = "none"
        data = appier.legacy.urlencode(values)
        url = url + "?" + data
        return url

    def oauth_access(self, code):
        url = self.api_url + "oauth2/token"
        contents = self.post(
            url,
            token = False,
            client_id = self.client_id,
            client_secret = self.client_secret,
            grant_type = "authorization_code",
            redirect_uri = self.redirect_url,
            code = code
        )
        self.access_token = contents["access_token"]
        self.refresh_token = contents.get("refresh_token", None)
        self.trigger("access_token", self.access_token)
        self.trigger("refresh_token", self.refresh_token)
        return self.access_token

    def oauth_refresh(self):
        url = self.api_url + "oauth2/token"
        contents = self.post(
            url,
            callback = False,
            token = False,
            client_id = self.client_id,
            client_secret = self.client_secret,
            grant_type = "refresh_token",
            redirect_uri = self.redirect_url,
            refresh_token = self.refresh_token
        )
        self.access_token = contents["access_token"]
        self.trigger("access_token", self.access_token)
        return self.access_token
