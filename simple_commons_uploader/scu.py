import argparse
import getpass
import re
from datetime import date, datetime
from pathlib import Path

from PIL import ExifTags, Image

# workaround for ModuleNotFound errors
if __name__ == '__main__':
    from wiki import Wiki, ColorLog
    from wgen import Wgen
else:
    from simple_commons_uploader.wiki import Wiki, ColorLog
    from simple_commons_uploader.wgen import Wgen


def main():
    MTC_FILE = Path.home() / ".scu.px.txt"

    cli_parser = argparse.ArgumentParser(description="Simple Commons Uploader")
    cli_parser.add_argument('dirs', metavar='folders', type=str, nargs='*', help='folders with files to upload')
    cli_parser.add_argument('--user', type=str, help="username to use")
    cli_parser.add_argument('--pw', type=str, help="password to use")
    cli_parser.add_argument("-i", action='store_true', help="force interactive login")
    cli_parser.add_argument("--wgen", action='store_true', help="run wgen password manager")
    args = cli_parser.parse_args()

    if args.wgen:
        Wgen.setup(MTC_FILE, False)
        return

    wiki = Wiki("commons.wikimedia.org")
    if args.i:
        wiki.login(input("Please login to continue.\nUsername: "), getpass.getpass())
    elif args.user:
        if not args.pw:
            ColorLog.error("You didn't specify a password, --pw")
            return

        wiki.login(args.user, args.pw)
    elif MTC_FILE.is_file():
        pxd = Wgen.load_px(MTC_FILE)
        if not pxd:
            ColorLog.error(f"Please run with --wgen option or remove {MTC_FILE} from your home directory")
        wiki.login(*pxd.popitem())
    else:
        cli_parser.print_help()
        return

    if not args.dirs:
        ColorLog.warn("You didn't specify and directories to upload!  Goodbye.")
        return

    ext_list = ["." + e for e in wiki.acceptable_file_extensions()]

    tpl = "=={{{{int:filedesc}}}}==\n{{{{Information\n|description={}\n|date={}\n|source={{{{Own}}}}\n|author=~~~\n}}}}\n\n" + \
        "=={{{{int:license-header}}}}==\n{{{{Self|Cc-by-sa-4.0}}}}\n\n[[Category:{}]]\n[[Category:Files by {}]]"

    for d in args.dirs:
        base_dir = Path(d)
        if not base_dir.is_dir():
            continue

        i = 1
        fails = []
        for f in base_dir.iterdir():
            if not f.is_file() or not f.suffix.lower() in ext_list:
                continue

            timestamp = None
            try:
                with Image.open(f) as img:
                    exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
                if "DateTimeOriginal" in exif:
                    dto = exif["DateTimeOriginal"]

                    if re.match(r"\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}", dto):
                        d, t = dto.split()
                        timestamp = d.replace(":", "-") + " " + t

            except Exception as e:
                ColorLog.warn(f"Could not parse EXIF for {f}: {e}")

            desc = tpl.format(base_dir.name, timestamp or f"{datetime.fromtimestamp(f.stat().st_mtime):%Y-%m-%d %H:%M:%S}", base_dir.name, wiki.username)
            if not wiki.upload(str(f), f"{base_dir.name} {i} {date.today()}{f.suffix.lower()}", desc, ""):
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
