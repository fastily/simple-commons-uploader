import argparse
import os
import re

from datetime import date, datetime

from wiki import Wiki
from wgen import Wgen


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


cli_parser = argparse.ArgumentParser(description="Simple Commons Uploader")
cli_parser.add_argument('dirs', metavar='folders', type=str, nargs='+', help='folders with files to upload')
cli_parser.add_argument('--user', type=str, default="FSock")
cli_parser.add_argument('--pw', type=str, default="")
args = cli_parser.parse_args()


wiki = Wiki("en.wikipedia.org")
if args.user: ## FIXME
    if args.pw:
        wiki.login(args.user, args.pw)
    else:
        wiki.login(args.user, Wgen.px_for(args.user))

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