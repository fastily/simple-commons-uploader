import argparse
import os
import re
import getpass

from datetime import date, datetime

# workaround for ModuleNotFound errors
if __name__ == '__main__':
    from wiki import Wiki, ColorLog
    from wgen import Wgen
else:
    from simple_commons_uploader.wiki import Wiki, ColorLog
    from simple_commons_uploader.wgen import Wgen


def main():
    MTC_FILE = os.path.join(os.path.expanduser("~"), ".scu.px.txt")

    def listdir_fullpath(d):
        return [os.path.join(d, f) for f in os.listdir(d)]

    cli_parser = argparse.ArgumentParser(description="Simple Commons Uploader")
    cli_parser.add_argument('dirs', metavar='folders', type=str, nargs='*', help='folders with files to upload')
    cli_parser.add_argument('--user', type=str, help="username to use")
    cli_parser.add_argument('--pw', type=str, help="password to use")
    cli_parser.add_argument("-i", action='store_true', help="force interactive login")
    cli_parser.add_argument("--wgen", action='store_true', help="run wgen password manager")
    args = cli_parser.parse_args()

    if args.wgen:
        Wgen.setup(out_file=MTC_FILE, allow_continue=False)
        exit()

    wiki = Wiki("commons.wikimedia.org")
    if args.i:
        print("Please login to continue.")
        u = input("Username: ")
        p = getpass.getpass()
        wiki.login(u, p)
    elif args.user:
        if not args.pw:
            ColorLog.error("You didn't specify a password, --pw")
            exit()

        wiki.login(args.user, args.pw)
    elif os.path.isfile(MTC_FILE):
        pxd = Wgen.load_px(px_file=MTC_FILE)
        if not pxd:
            ColorLog.error("Please run with --wgen option or remove {} from your home directory".format(MTC_FILE))

        k, v = pxd.popitem()
        wiki.login(k, v)
    else:
        cli_parser.print_help()
        exit()

    if not args.dirs:
        ColorLog.warn(
            "You didn't specify and directories to upload!  Goodbye.")
        exit()

    pattern = re.compile(
        "(?i).+\\.({})".format("|".join(wiki.acceptable_file_extensions())))

    tpl = "=={{{{int:filedesc}}}}==\n{{{{Information\n|description={}\n|date={}\n|source={{{{Own}}}}\n|author=~~~\n}}}}\n\n" + \
        "=={{{{int:license-header}}}}==\n{{{{Self|Cc-by-sa-4.0}}}}\n\n[[Category:{}]]\n[[Category:Files by {}]]"

    for d in args.dirs:
        if not os.path.isdir(d):
            continue

        i = 1
        dir_base = os.path.basename(os.path.normpath(d))

        fails = []
        for f in [fn for fn in listdir_fullpath(d) if pattern.match(fn)]:
            title = "{} {} {}{}".format(dir_base, i, str(
                date.today()), os.path.splitext(f)[1].lower())
            desc = tpl.format(
                dir_base, f"{datetime.fromtimestamp(os.path.getmtime(f)):%Y-%m-%d %H:%M:%S}", dir_base, wiki.username)
            if not wiki.upload(f, title, desc, ""):
                fails.append(f)
            i += 1

    if fails:
        print("Failed to upload:")
        for f in fails:
            print(f)
    else:
        print("Complete, with no failures")

if __name__ == '__main__':
    main()
    