import requests
import os
import datetime


DEFAULT_PARAMS = {"format": "json", "formatversion": "2"}

CHUNKSIZE = 1024 * 1024 * 4


class Wiki:
    def __init__(self, domain, username=None, password=None):
        self.endpoint = f"https://{domain}/w/api.php"
        self.domain = domain
        self.client = requests.Session()
        self.username = username

        self.csrf_token = None

        if username and password:
            self.login(username, password)

    def __make_params(self, action, pl={}):
        global DEFAULT_PARAMS
        d = DEFAULT_PARAMS.copy()

        d["action"] = action
        d.update(pl)
        return d

    def acceptable_file_extensions(self):
        """Gets acceptable file extensions which may be uploaded to this Wiki.  Returns a list with acceptable extensions"""

        ColorLog.info("Fetching a list of acceptable file upload extensions", self)

        response = self.client.get(self.endpoint, params=self.__make_params("query", {"meta": "siteinfo", "siprop": "fileextensions"}))
        return {jo["ext"] for jo in response.json()["query"]['fileextensions']}

    def login(self, username, password):
        """Logs a user in.

        :param username: the username to use
        :param password: The password to use
        """
        ColorLog.info("Try login for " + username, self)

        response = self.client.post(self.endpoint, params=self.__make_params("login"), data={
                                    "lgname": username, "lgpassword": password, "lgtoken": self.get_tokens()["logintoken"]})

        self.username = response.json()["login"]["lgusername"]
        self.csrf_token = self.get_tokens()['csrftoken']

        return True

    def get_tokens(self):
        """Gets CSRF and Login tokens.  Returns a dict with keys csrftoken and logintoken"""
        return self.client.get(self.endpoint, params=self.__make_params("query", {"meta": "tokens", "type": "csrf|login"})).json()['query']['tokens']

    def upload(self, path, title, desc, summary):
        """Uploads a file.  Returns True on success

        :param path: the local path to the file to upload
        :param title: The title to upload the file to, excluding "File:" namespace
        :param desc: The text of the description page
        :param summary: The edit summary to use
        """

        fsize = os.path.getsize(path)
        total_chunks = fsize // CHUNKSIZE + 1

        ColorLog.info("Uploading " + path, self)

        data = DEFAULT_PARAMS.copy()
        data.update({"filename": title, "offset": '0', "ignorewarnings": "1", "filesize": str(fsize), "token": self.csrf_token, "stash": "1"})

        with open(path, 'rb') as f:
            buffer = f.read(CHUNKSIZE)
            chunk_count = 0

            err_count = 0
            while True:
                if err_count > 5:
                    ColorLog.error(f"Encountered {err_count} errors, aborting", self)
                    break

                ColorLog.fyi(f"Uploading chunk [{chunk_count + 1} of {total_chunks}] of '{path}'", self)

                response = self.client.post(self.endpoint, params={"action": "upload"}, data=data, files={
                                            'chunk': (os.path.basename(path), buffer, "multipart/form-data")}, timeout=420)
                if not response:
                    ColorLog.error("Did not get a response back from the server, retrying...", self)
                    err_count += 1
                    continue

                response = response.json()
                if "error" in response:
                    ColorLog.error(response['error']['info'], self)
                    err_count += 1
                    continue

                data['filekey'] = response["upload"]["filekey"]
                chunk_count += 1
                data['offset'] = str(CHUNKSIZE * chunk_count)

                buffer = f.read(CHUNKSIZE)
                if not buffer:
                    break

        if "filekey" not in data:
            return False

        ColorLog.info(f"Unstashing {data['filekey']} as {title}", self)
        pl = {"filename": title, "text": desc, "comment": summary, "filekey": data['filekey'], "ignorewarnings": "1", "token": self.csrf_token}
        pl.update(DEFAULT_PARAMS)
        response = self.client.post(self.endpoint, params={"action": "upload"}, data=pl, timeout=420).json()

        if 'error' in response:
            ColorLog.error(response['error']['info'], self)
            return False

        return response['upload']['result'] == "Success"


class ColorLog:

    @staticmethod
    def __log(color_code, level, msg, wiki=None):
        """Prints out a message to std out
            :param color_code: The ANSI color to print (1-9)
            :param level: The level string (e.g. WARN, INFO, ERROR)
            :param msg: the mesage to print
            :param wiki: the Wiki to generate a prefix with (optional)
        """
        prefix = f"[{wiki.username or '<Anonymous>'} @ {wiki.domain}]: " if wiki else ""
        print(f"{datetime.datetime.now():%b %d, %Y %I:%M:%S %p}\n{level}: \033[3{color_code}m{prefix}{msg}\033[0m")

    @staticmethod
    def warn(msg, wiki=None):
        """Prints out a warning message.
            :param msg: the mesage to print
            :param wiki: the Wiki to generate a prefix with (optional)
        """
        ColorLog.__log(3, "WARN", msg, wiki)

    @staticmethod
    def info(msg, wiki=None):
        """Prints out an info message.
            :param msg: the mesage to print
            :param wiki: the Wiki to generate a prefix with (optional)
        """
        ColorLog.__log(2, "INFO", msg, wiki)

    @staticmethod
    def error(msg, wiki=None):
        """Prints out an error message.
            :param msg: the mesage to print
            :param wiki: the Wiki to generate a prefix with (optional)
        """
        ColorLog.__log(1, "ERROR", msg, wiki)

    @staticmethod
    def fyi(msg, wiki=None):
        """Prints out an FYI message.
            :param msg: the mesage to print
            :param wiki: the Wiki to generate a prefix with (optional)
        """
        ColorLog.__log(6, "FYI", msg, wiki)
