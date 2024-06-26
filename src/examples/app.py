#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Dropbox API
# Copyright (c) 2008-2024 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import tempfile

import appier

from . import base


class DropboxApp(appier.WebApp):

    def __init__(self, *args, **kwargs):
        appier.WebApp.__init__(self, name="dropbox", *args, **kwargs)

    @appier.route("/", "GET")
    def index(self):
        return self.me()

    @appier.route("/me", "GET")
    def me(self):
        url = self.ensure_api()
        if url:
            return self.redirect(url)
        api = self.get_api()
        account = api.self_user()
        return account

    @appier.route("/files/insert/<str:message>", "GET")
    def file_insert(self, message):
        url = self.ensure_api()
        if url:
            return self.redirect(url)
        api = self.get_api()
        path = self.field("path", "/hello")
        message = appier.legacy.bytes(message, encoding="utf-8", force=True)
        contents = api.session_start_file()
        session_id = contents["session_id"]
        contents = api.session_finish_file(session_id, data=message, path=path)
        return contents

    @appier.route("/files/large/<str:message>", "GET")
    def file_large(self, message):
        url = self.ensure_api()
        if url:
            return self.redirect(url)
        api = self.get_api()
        path = self.field("path", None)
        message = appier.legacy.bytes(message, encoding="utf-8", force=True)
        fd, file_path = tempfile.mkstemp()
        try:
            os.write(fd, message)
        finally:
            os.close(fd)
        path = path or "/" + os.path.basename(file_path)
        try:
            contents = api.upload_large_file(file_path, path)
        finally:
            os.remove(file_path)
        return contents

    @appier.route("/files/download", "GET")
    def file_download(self):
        url = self.ensure_api()
        if url:
            return self.redirect(url)
        api = self.get_api()
        path = self.field("path", mandatory=True)
        contents, result = api.download_file(path)
        content_type = appier.FileTuple.guess(result["name"])
        if content_type:
            self.request.set_content_type(content_type)
        return contents

    @appier.route("/files/upload", "GET")
    def file_upload(self):
        url = self.ensure_api()
        if url:
            return self.redirect(url)
        api = self.get_api()
        path = self.field("path", mandatory=True)
        target = self.field("target", None)
        target = target or "/" + os.path.basename(path)
        contents = api.upload_large_file(path, target)
        return contents

    @appier.route("/folders/list", "GET")
    def folder_list(self):
        url = self.ensure_api()
        if url:
            return self.redirect(url)
        api = self.get_api()
        path = self.field("path", "")
        contents = api.list_folder_file(path)
        return contents

    @appier.route("/links/share", "GET")
    def link_share(self):
        url = self.ensure_api()
        if url:
            return self.redirect(url)
        api = self.get_api()
        path = self.field("path", "/hello")
        contents = api.create_shared_link(path)
        return contents

    @appier.route("/logout", "GET")
    def logout(self):
        return self.oauth_error(None)

    @appier.route("/oauth", "GET")
    def oauth(self):
        code = self.field("code")
        error = self.field("error")
        appier.verify(
            not error,
            message="Invalid OAuth response (%s)" % error,
            exception=appier.OperationalError,
        )
        api = self.get_api()
        access_token = api.oauth_access(code)
        self.session["dropbox.access_token"] = access_token
        self.session["dropbox.refresh_token"] = api.refresh_token
        return self.redirect(self.url_for("dropbox.index"))

    @appier.exception_handler(appier.OAuthAccessError)
    def oauth_error(self, error):
        if "dropbox.access_token" in self.session:
            del self.session["dropbox.access_token"]
        if "dropbox.refresh_token" in self.session:
            del self.session["dropbox.refresh_token"]
        return self.redirect(self.url_for("dropbox.index"))

    def ensure_api(self):
        access_token = appier.conf("DROPBOX_TOKEN", None)
        access_token = self.session.get("dropbox.access_token", access_token)
        if access_token:
            return
        api = base.get_api()
        return api.oauth_authorize()

    def get_api(self):
        access_token = appier.conf("DROPBOX_TOKEN", None)
        refresh_token = appier.conf("DROPBOX_REFRESH", None)
        access_token = self.session and self.session.get(
            "dropbox.access_token", access_token
        )
        refresh_token = self.session and self.session.get(
            "dropbox.refresh_token", refresh_token
        )
        api = base.get_api()
        api.access_token = access_token
        if refresh_token:
            api.refresh_token = refresh_token
        return api


if __name__ == "__main__":
    app = DropboxApp()
    app.serve()
else:
    __path__ = []
