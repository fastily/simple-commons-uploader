import argparse
import logging
import re

from datetime import date, datetime
from pathlib import Path
from textwrap import dedent

from PIL import Image
from rich.logging import RichHandler

from pwiki.wiki import Wiki

log = logging.getLogger(__name__)


def _main() -> None:
    """Main driver, to be run if this script is invoked directly."""

    for lg in (logging.getLogger("pwiki"), log):
        lg.addHandler(RichHandler(rich_tracebacks=True))
        lg.setLevel(logging.INFO)

    cli_parser = argparse.ArgumentParser(description="Simple Commons Uploader")
    cli_parser.add_argument('-u', type=str, default="Fastily", metavar="username", help="username to use")
    cli_parser.add_argument('dirs', metavar='folders', type=Path, nargs='*', help='folders with files to upload')
    args = cli_parser.parse_args()

    if not args.dirs:
        log.critical("You didn't specify and directories to upload!")
        return

    wiki = Wiki("commons.wikimedia.org", args.u)
    ext_list = {"." + e for e in wiki.uploadable_filetypes()}
    fails = []

    for base_dir in args.dirs:
        if not base_dir.is_dir():
            continue

        i = 1
        for f in base_dir.iterdir():
            if not f.is_file() or (ext := f.suffix.lower()) not in ext_list:
                continue

            # date
            timestamp = None
            if ext in (".jpg", ".jpeg"):
                try:
                    with Image.open(f) as img:
                        if (dto := img.getexif().get(306)) and re.match(r"\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}", dto):
                            d, t = dto.split()
                            timestamp = f"{d.replace(':', '-')} {t}"
                except Exception as e:
                    log.warning("Could not parse EXIF for %s", f, exc_info=True)

            # base_desc, cat
            if "_" in base_dir.name:
                b, cat = [s.strip() for s in base_dir.name.split("_", 1)]
            else:
                b = cat = base_dir.name

            desc = dedent(f"""\
            =={{{{int:filedesc}}}}==
            {{{{Information
            |description={b}
            |date={timestamp or datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
            |source={{{{Own}}}}
            |author=~~~
            }}}}

            =={{{{int:license-header}}}}==
            {{{{Self|Cc-by-sa-4.0}}}}
            
            [[Category:{cat}]]
            [[Category:Files by {wiki.username}]]""")

            if not wiki.upload(f, f"{b} {i} {date.today()}{ext}", desc):
                fails.append(f)
            i += 1

    if fails:
        log.warning("Failed to upload %d files: %s", len(fails), fails)
    else:
        log.info("Finished with no failures")

    wiki.save_cookies()


if __name__ == '__main__':
    _main()
