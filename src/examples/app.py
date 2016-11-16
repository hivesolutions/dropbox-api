#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Dropbox API
# Copyright (c) 2008-2016 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

import base

class DropboxApp(appier.WebApp):

    def __init__(self, *args, **kwargs):
        appier.WebApp.__init__(
            self,
            name = "dropbox",
            *args, **kwargs
        )

    @appier.route("/", "GET")
    def index(self):
        return self.me()

    @appier.route("/me", "GET")
    def me(self):
        api = self.get_api()
        account = api.self_user()
        return account

    @appier.route("/files", "GET")
    def files(self):
        url = self.ensure_api()
        if url: return self.redirect(url)
        api = self.get_api()
        contents = api.list_drive()
        return contents

    @appier.route("/files/<std:id>", "GET")
    def file(self, id):
        url = self.ensure_api()
        if url: return self.redirect(url)
        api = self.get_api()
        contents = api.get_drive(id)
        return contents

    @appier.route("/files/insert/<str:message>", "GET")
    def file_insert(self, message):
        url = self.ensure_api()
        if url: return self.redirect(url)
        api = self.get_api()
        contents = api.insert_drive(
            message,
            content_type = "text/plain",
            title = message
        )
        return contents

    def ensure_api(self):
        access_token = self.session.get("gg.access_token", None)
        if access_token: return
        api = base.get_api()
        return api.oauth_authorize()

    def get_api(self):
        api = base.get_api()
        return api

if __name__ == "__main__":
    app = DropboxApp()
    app.serve()
