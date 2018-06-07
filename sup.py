import argparse
import os
import re
import getpass

from datetime import date, datetime

from wiki import Wiki
from wgen import Wgen

MTC_FILE=".mtc.px.txt"

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


cli_parser = argparse.ArgumentParser(description="Simple Commons Uploader")
cli_parser.add_argument('dirs', metavar='folders', type=str, nargs='*', help='folders with files to upload')
cli_parser.add_argument('--user', type=str, help="username to use")
cli_parser.add_argument('--pw', type=str, help="password to use")
cli_parser.add_argument("-i",  action='store_true', help="force interactive login")
cli_parser.add_argument("--wgen",  action='store_true', help="run wgen password manager")
args = cli_parser.parse_args()

if args.wgen:
    Wgen.setup(out_file=MTC_FILE, allow_continue=False)
    exit()


wiki = Wiki("en.wikipedia.org")
if args.i:
    print("Please login to continue.")
    u = input("Username: ")
    p = getpass.getpass()
    wiki.login(u, p)
elif args.user:
    if not args.pw:
        print("ERROR: You didn't specify a password, --pw")
        exit()

    wiki.login(args.user, args.pw)
elif os.path.isfile(MTC_FILE):
    pxd = Wgen.load_px(px_file=MTC_FILE)
    if not pxd:
        print("ERROR: please run with --wgen option or remove {} from your home directory".format(MTC_FILE))

    k, v = pxd.popitem()
    wiki.login(k, v)
else:
    cli_parser.print_help()
    exit()


if not args.dirs:
    print("You didn't specify and directories to upload!  Goodbye.")
    exit()

pattern = re.compile("(?i).+\\.({})".format("|".join(wiki.acceptable_file_extensions())))

tpl = """=={{{{int:filedesc}}}}==
{{{{Information
|description={}
|date={}
|source={{{{Own}}}}
|author=~~~
}}}}

=={{{{int:license-header}}}}==
{{{{Self|Cc-by-sa-4.0}}}}

[[Category:{}]]
[[Category:Files by {}]]"""


for d in args.dirs:
    i = 1
    dir_base = os.path.basename(os.path.normpath(d))

    fails = []
    for f in [ fn for fn in listdir_fullpath(d) if pattern.match(fn) ]:
        title = "{} {} {}{}".format(dir_base, str(date.today()), i, os.path.splitext(f)[1])
        desc = tpl.format(dir_base, datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S"), dir_base, wiki.username)
        if not wiki.upload(f, title, desc, ""):
            fails.append(f)
        i+=1

    if fails:
        print("Failed to upload:")
        for f in fails:
            print(f)
    else:
        print("All done!")