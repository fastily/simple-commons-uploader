import base64
import os
import re
import getpass

class Wgen:

    @staticmethod
    def load_px(px_file=".px.txt"):
        """Loads the specified password file if it exists.  Returns a dictionary with username/passwords that were found
        
        :param load_px: The path to the password file
        """
        pxd = {}

        pxf = os.path.join(os.path.expanduser("~"), px_file)
        if os.path.isfile(pxf):
            with open(pxf, "r") as f:
                for line in base64.b64decode(f.read().encode("utf-8")).decode("utf-8").strip().splitlines():
                    u, p = line.split("\t")
                    pxd[u] = p
                    
        return pxd


    @staticmethod
    def setup(out_file=".px.txt", allow_continue=True):
        """Interactively creates a password file.
        
        :param out_file: The path to create the password file at.  CAVEAT: If a file exists at this location exists it will be overwritten.
        :param allow_continue: Set True to allow user to enter more than one user-pass combo.
        """
        pxl = {}

        while True:
            print("Please enter the username/password combo(s) you would like to use.")
            u = input("Username: ")
            p = getpass.getpass()
            confirm_p = getpass.getpass("Confirm Password: ")

            if p != confirm_p:
                print("ERROR: Entered passwords do not match")
                if not re.match("(?i)(y|yes)", input("Try again? (y/N): ").lower()):
                    break
            else:
                pxl[u] = p

                if not allow_continue or not re.match("(?i)(y|yes)", input("Continue? (y/N): ").lower()):
                    break

        if not pxl:
            print("WARNING: You did not make any entries.  Doing nothing.")
            return

        out = ""
        for k,v in pxl.items():
            out += "{}\t{}\n".format(k,v)

        with open(out_file, "w") as f:
            f.write(base64.b64encode(out.encode("utf-8")).decode("utf-8"))

        print("Successfully created '{}'".format(out_file))