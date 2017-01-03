#!/usr/bin/python3
from bottle import post, get, run, request, static_file, redirect
import os
import shutil

APPLICATION = 'CodersOS-image-server'
APPDATA_ROOT = os.environ.get('APPDATA', '/var/' + APPLICATION)
APPDATA = os.path.join(APPDATA_ROOT, APPLICATION)
HERE = os.path.dirname(__file__) or os.getcwd()
ZIP_PATH = "/" + APPLICATION + ".zip"

# --------------------- POST /create ---------------------

REDIRECT = "redirect"
COMMANDS = "commands"
NAME = "name"
COMMAND = "command"

def is_url(url):
    return url.startswith("http://") or url.startswith("https://")

def verify_specification(specification):
    assert isinstance(specification, dict), "The image specification must be an object"
    assert REDIRECT in specification, "\"redirect\" must be an attribute of the specification."
    assert is_url(specification[REDIRECT]), "The value of \"redirect\" must be a url."
    assert COMMANDS in specification, "\"commands\" must be an attribute of the specification."
    specification_commands = specification[COMMANDS]
    assert isinstance(specification_commands, list), "The value of \"commands\" must be a list."
    for index, command in enumerate(specification_commands):
        assert isinstance(command, dict), "Command {} must be an object.".format(index)
        assert NAME in command, "Command {} must have an attribute \"name\"."
        assert isinstance(command[NAME], str), "The value of \"name\" of command {} must be a string.".format(index)
        assert COMMAND in command, "Command {} must have an attribute \"command\"."
        assert isinstance(command[COMMAND], str), "The value of \"command\" of command {} must be a string.".format(index)
        
@post("/create")
def create_image():
    specification = request.json()
    verify_specification(specification)
    



# --------------------- AGPL Source ---------------------

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