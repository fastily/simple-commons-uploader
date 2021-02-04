import argparse
import getpass
import logging
import re

from datetime import date, datetime
from pathlib import Path
from textwrap import dedent

from PIL import ExifTags, Image
from rich.logging import RichHandler

from pwiki import wgen
from pwiki.wiki import Wiki

log = logging.getLogger(__name__)

MTC_FILE = Path.home() / ".scu.px.txt"


def _main():
    for lg in (logging.getLogger("pwiki"), log):
        lg.addHandler(RichHandler(rich_tracebacks=True))
        lg.setLevel("INFO")

    cli_parser = argparse.ArgumentParser(description="Simple Commons Uploader")
    cli_parser.add_argument('--user', type=str, help="username to use")
    cli_parser.add_argument('--pw', type=str, help="password to use")
    cli_parser.add_argument("-i", action='store_true', help="force interactive login")
    cli_parser.add_argument("--wgen", action='store_true', help="run wgen password manager")
    cli_parser.add_argument('dirs', metavar='folders', type=Path, nargs='*', help='folders with files to upload')
    args = cli_parser.parse_args()

    if args.wgen:
        wgen.setup_px(MTC_FILE, False)
        return

    wiki = Wiki("commons.wikimedia.org")
    if args.i:
        wiki.login(input("Please login to continue.\nUsername: "), getpass.getpass())
    elif args.user:
        if not args.pw:
            log.critical("No password specified, please pass the --pw flag with a pasword.")
            return
        wiki.login(args.user, args.pw)
    elif MTC_FILE.is_file():
        wiki.login(*wgen.load_px(MTC_FILE).popitem())
    else:
        cli_parser.print_help()
        return

    if not args.dirs:
        log.critical("You didn't specify and directories to upload!")
        return

    ext_list = {"." + e for e in wiki.uploadable_filetypes()}
    fails = []

    for base_dir in args.dirs:
        if not base_dir.is_dir():
            continue

        i = 1
        for f in base_dir.iterdir():
            ext = f.suffix.lower()
            if not f.is_file() or ext not in ext_list:
                continue

            timestamp = None
            if ext in (".jpg", ".jpeg"):
                try:
                    with Image.open(f) as img:
                        if dto := next((v for k, v in img.getexif().items() if ExifTags.TAGS.get(k) == "DateTimeOriginal" and re.match(r"\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}", v)), None):
                            d, t = dto.split()
                            timestamp = f"{d.replace(':', '-')} {t}"
                except Exception as e:
                    log.warn("Could not parse EXIF for %s", f, exc_info=True)

            desc = f"""\
            =={{{{int:filedesc}}}}==
            {{{{Information
            |description={base_dir.name}
            |date={timestamp or datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
            |source={{{{Own}}}}
            |author=~~~
            }}}}

            =={{{{int:license-header}}}}==
            {{{{Self|Cc-by-sa-4.0}}}}
            
            [[Category:{base_dir.name}]]
            [[Category:Files by {wiki.username}]]"""

            if not wiki.upload(f, f"{base_dir.name} {i} {date.today()}{ext}", dedent(desc)):
                fails.append(f)
            i += 1

    if fails:
        log.warn("Failed to upload %d files: %s", len(fails), fails)
    else:
        log.info("Finished with no failures")


if __name__ == '__main__':
    _main()
