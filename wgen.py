import base64
import os

class Wgen:
    @staticmethod
    def px_for(user):
        pxd = {}

        pxf = os.path.join(os.path.expanduser("~"), ".px.txt")
        if os.path.isfile(pxf):
            with open(pxf, "r") as f:
                for line in base64.b64decode(f.read().encode("utf-8")).decode("utf-8").strip().splitlines():
                    u, p = line.split("\t")
                    pxd[u] = p
                    
        return pxd.get(user, None)


if __name__ == "__main__":
    # base64.b64encode("nyah".encode("utf-8")).decode("utf-8")
    pass