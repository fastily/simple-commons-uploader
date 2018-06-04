import argparse
import os
import re

from datetime import date, datetime

from wiki import Wiki

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('dirs', metavar='D', type=str, nargs='+', help='directories with files to upload')
args = cli_parser.parse_args()

if not args.dirs:
    print("You need to specify at least one directory!")
    exit()


wiki = Wiki("en.wikipedia.org", "", "")

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
    i = 0
    dir_base = os.path.basename(os.path.normpath(d))

    for f in [ fn for fn in listdir_fullpath(d) if pattern.match(fn) ]:
        wiki.upload(f, "{} {} {}.{}".format(dir_base, str(date.today()), i, os.path.splitext(f)[1]), tpl.format(dir_base, datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S"), dir_base, wiki.username), "")
        i+=1