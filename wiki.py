import requests
import os

DEFAULT_PARAMS={"format": "json", "formatversion": "2"}

CHUNKSIZE = 1024 * 1024 * 1

class Wiki:
    def __init__(self, domain, username=None, password=None):
        self.endpoint="https://{}/w/api.php".format(domain)
        self.client = requests.Session()
        self.username = username

        self.csrf_token = None

        if username != None and password != None:
            self.login(username, password)


    def __make_params(self, action, pl={}):
        global DEFAULT_PARAMS
        d = DEFAULT_PARAMS.copy()

        d["action"] = action
        d.update(pl)
        return d


    def acceptable_file_extensions(self):
        """Gets acceptable file extensions which may be uploaded to this Wiki.  Returns a list with acceptable extensions"""
        response = self.client.get(self.endpoint, params=self.__make_params("query", {"meta": "siteinfo", "siprop": "fileextensions"}))
        return [ jo["ext"] for jo in response.json()["query"]['fileextensions'] ]


    def login(self, username, password):
        """Logs a user in.
        
        :param username: the username to use
        :param password: The password to use
        """
        response = self.client.post(self.endpoint, params=self.__make_params("login"), data={"lgname": username, "lgpassword": password, "lgtoken": self.get_tokens()["logintoken"]})

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
        :summary: The edit summary to use
        """

        fsize = os.path.getsize(path)
        total_chunks = fsize // CHUNKSIZE + 1

        print("Uploading {} to {}".format(path, title))

        data = DEFAULT_PARAMS.copy()
        data.update( {"filename": title, "offset": '0', "ignorewarnings": "1", "filesize": str(fsize), "token": self.csrf_token, "stash": "1"} )

        with open(path, 'rb') as f:
            buffer = f.read(CHUNKSIZE)
            chunk_count = 0

            while True:
                print("Uploading chunk {} of {}".format(chunk_count + 1, total_chunks))
                response = self.client.post(self.endpoint, params={"action": "upload"}, data=data, files={'chunk':(os.path.basename(path), buffer, "multipart/form-data")})
                data['filekey'] = response.json()["upload"]["filekey"]

                chunk_count+=1
                data['offset'] = str(CHUNKSIZE * chunk_count)

                buffer = f.read(CHUNKSIZE)
                if not buffer:
                    break

        print("Unstashing {} as {}".format(data['filekey'], title))
        pl = {"filename": title, "text": desc, "comment": summary, "filekey": data['filekey'], "ignorewarnings": "1", "token": self.csrf_token}
        pl.update(DEFAULT_PARAMS)
        response = self.client.post(self.endpoint, params={"action": "upload"}, data=pl)
        
        return response.json()['upload']['result'] == "Success"