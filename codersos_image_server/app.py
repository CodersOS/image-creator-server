#!/usr/bin/python3
from bottle import post, get, run, request, static_file, redirect
import os
import sys
import shutil

APPLICATION = 'kindermalerei'
APPDATA_ROOT = os.environ.get('APPDATA', '/var/' + APPLICATION)
APPDATA = os.path.join(APPDATA_ROOT, APPLICATION)
HERE = os.path.dirname(__file__) or os.getcwd()
ZIP_PATH = "/" + APPLICATION + ".zip"

@get('/source')
def get_source_redirect():
    """Download the source of this application."""
    redirect(ZIP_PATH)

@get(ZIP_PATH)
def get_source():
    """Download the source of this application."""
    # from http://stackoverflow.com/questions/458436/adding-folders-to-a-zip-file-using-python#6511788
    path = (shutil.make_archive("/tmp/" + APPLICATION, "zip", HERE))
    return static_file(path, root="/")

if __name__ == "__main__":
    run(host='', port=80, debug=True)