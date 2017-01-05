#!/usr/bin/python3
from bottle import post, get, run, request, static_file, redirect, abort, response
import os
import shutil
from .build import ParallelBuild
from .image import Image
from pprint import pprint

APPLICATION = 'CodersOS-image-server'
APPDATA_ROOT = os.environ.get('APPDATA', '/var/' + APPLICATION)
APPDATA = os.path.join(APPDATA_ROOT, APPLICATION)
HERE = os.path.dirname(__file__) or os.getcwd()
ZIP_PATH = "/" + APPLICATION + ".zip"
BASE_IMAGE = "codersos/linux-iso-creator"


# --------------------- enable ayax access ---------------------

def enable_cors():
    # set CORS headers
    # from http://stackoverflow.com/a/17262900/1320237
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

# --------------------- POST /create ---------------------

REDIRECT = "redirect"
COMMANDS = "commands"
NAME = "name"
COMMAND = "command"
ARGUMENTS = "arguments"
STATUS = "status"

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
        assert ARGUMENTS in command, "Command {} must have an attribute \"arguments\"."
        assert isinstance(command[ARGUMENTS], list), "The value of \"arguments\" of command {} must be a list.".format(index)
        assert all(map(lambda argument: isinstance(argument, str), command[ARGUMENTS])), "All arguments in comand {} must be strings.".format(index)
        
builds = {}
next_build_id = 0

@post("/create")
def create_image():
    global next_build_id
    specification = request.json
    pprint(specification)
    verify_specification(specification)
    build = ParallelBuild(Image(BASE_IMAGE), specification[COMMANDS])
    build.start()
    builds[next_build_id] = build
    next_build_id += 1
    redirect_url = specification[REDIRECT]
    if not "?" in redirect_url:
        redirect_url += "?"
    elif redirect_url.find("?") != len(redirect_url) - 1:
        redirect_url += "&"
    redirect_url += "status=/status/{}".format(next_build_id)
    redirect(redirect_url)
    

# --------------------- Build Status ---------------------

@get("/status/<build_id:int>")
def get_status(build_id):
    enable_cors()
    if build_id not in builds:
        abort(404, '{"error": "Not found."}')
    build = builds[build_id]
    status = {}
    status[STATUS] = build_status = build.get_status_code()
    if build_status == "stopped" and build.get_iso_path() is not None:
        status["download"] = "/download/{}/CodersOS.iso".format(build_id)
    status["output"] = build.get_status()
    return status

@get("/download/<build_id:int>/<filename>")
def download(build_id, filename):
    enable_cors()
    if build_id not in builds:
        abort(404, '{"error": "Not found."}')
    build = builds[build_id]
    iso_path = build.get_iso_path()
    assert iso_path is not None
    return open(iso_path, "rb")


# --------------------- Status ---------------------

@get("/status")
def server_status():
    enable_cors()
    return {"status" : "ready", "priority" : 0}


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
    run(host='', port=80, debug=True, reload=True)