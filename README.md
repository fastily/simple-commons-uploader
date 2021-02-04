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
usage: scu [-h] [--user USER] [--pw PW] [-i] [--wgen] [folders [folders ...]]

Simple Commons Uploader

positional arguments:
  folders      folders with files to upload

optional arguments:
  -h, --help   show this help message and exit
  --user USER  username to use
  --pw PW      password to use
  -i           force interactive login
  --wgen       run wgen password manager
```

## Authentication/Login
The Simple Commons Uploader works with your normal password and [BotPasswords](https://commons.wikimedia.org/wiki/Special:BotPasswords).  

There are three ways to authenticate:
1. Interactively typing your credentials into the terminal, by running the program with the `-i` flag.
2. Specifying your credentials via the `--user` and `--pw` flags.
3. Using the Wgen setup utility by initially running the program with the `--wgen` flag.  This method has the advantage of saving your credentials so you won't have to type them in the next time you use the program.


## Behavior Details
The Simple Commons Uploader only uploads files in [these file formats](https://commons.wikimedia.org/wiki/Commons:File_types).  Any other file types will be skippied.

Uploaded files will be named based on local folder name.  For example, if your folder is called `Fancy pigeons`, contains jpgs of fancy pigeons, and today's date is 2018-01-01, then the resulting files will be named `File:Fancy pigeons 1 2018-01-01.jpg`, `File:Fancy pigeons 2 2018-01-01.jpg`, `File:Fancy pigeons 3 2018-01-01.jpg`, etc.