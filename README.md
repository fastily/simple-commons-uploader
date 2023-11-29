# Simple Commons Uploader
[![Python 3.9+](https://upload.wikimedia.org/wikipedia/commons/4/4f/Blue_Python_3.9%2B_Shield_Badge.svg)](https://www.python.org)
[![MediaWiki 1.35+](https://upload.wikimedia.org/wikipedia/commons/b/b3/Blue_MediaWiki_1.35%2B_Shield_Badge.svg)](https://www.mediawiki.org/wiki/MediaWiki)
[![License: GPL v3](https://upload.wikimedia.org/wikipedia/commons/8/86/GPL_v3_Blue_Badge.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

The Simple Commons Uploader makes it easy to batch upload your self-made photos and videos to the [Wikimedia Commons](https://commons.wikimedia.org/wiki/Main_Page).

⚠️ You must have an account on Wikimedia Commons to use this program.  Create an account by [going here](https://commons.wikimedia.org/wiki/Special:CreateAccount).

## Download
```bash
pip install simple-commons-uploader
```

## Usage
```
usage: __main__.py [-h] [-u username] [folders ...]

Simple Commons Uploader

positional arguments:
  folders      folders with files to upload

options:
  -h, --help   show this help message and exit
  -u username  username to use
```

## Authentication/Login
The Simple Commons Uploader works with your normal password and [BotPasswords](https://commons.wikimedia.org/wiki/Special:BotPasswords).  

👉 Password is set via env variable `<USERNAME>_PW`, such that `<USERNAME>` is the username of the bot in all caps.

## Behavior Details
The Simple Commons Uploader only uploads files in [these file formats](https://commons.wikimedia.org/wiki/Commons:File_types).  Any other file types will be skippied.

Uploaded files will be named based on local folder name.  For example, if your folder is called `Fancy pigeons`, contains jpgs of fancy pigeons, and today's date is 2018-01-01, then the resulting files will be named `File:Fancy pigeons 1 2018-01-01.jpg`, `File:Fancy pigeons 2 2018-01-01.jpg`, `File:Fancy pigeons 3 2018-01-01.jpg`, etc.

Uploaded files will be categorized using the same name as the containing folder on your computer.  To use a different category, add an `_` character to the end of the folder name, followed by the category (without the `Category` prefix) you would like to add.  For example, a folder with name `Fancy pigeons _ Gray birds` will cause `scu` to upload the files with a base name of `Fancy pigeons` and categorize them in `Category:Gray birds`.