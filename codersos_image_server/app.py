#!/usr/bin/python3
from bottle import post, get, run, request, static_file, redirect, abort
import os
import shutil
from .commander import ParallelCommander
from .image import Image

APPLICATION = 'CodersOS-image-server'
APPDATA_ROOT = os.environ.get('APPDATA', '/var/' + APPLICATION)
APPDATA = os.path.join(APPDATA_ROOT, APPLICATION)
HERE = os.path.dirname(__file__) or os.getcwd()
ZIP_PATH = "/" + APPLICATION + ".zip"
BASE_IMAGE = "codersos/ubuntu-remix"

# --------------------- POST /create ---------------------

REDIRECT = "redirect"
COMMANDS = "commands"
NAME = "name"
COMMAND = "command"
ARGUMENTS = "arguments"

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
        
commands = {}
next_command_id = 0

@post("/create")
def create_image():
    global next_command_id
    specification = request.json()
    verify_specification(specification)
    command = ParallelCommand(BASE_IMAGE, specification)
    command.start()
    commands[next_command_id] = command
    next_command_id += 1
    redirect_url = specification[REDIRECT]
    if not "?" in redirect_url:
        redirect_url += "?"
    elif redirect_url.find("?") != len(redirect_url) - 1:
        redirect_url += "&"
    redirect_url += "status=/status/{}".format(next_command_id)
    redirect(redirect_url)
    

# --------------------- Status ---------------------

@get("/status/<command_id>")
def get_status(command_id):
    if command_id not in commands:
        abort(404, '{"error": "Not found."}')
    command = commands[command_id]
    status = {}
    status[STATUS] = command_status = command.get_status_code()
    if command_status == "stopped" and command.get_iso_path() is not None:
        status["download"] = "/download/{}/CodersOS.iso".format(command_id)
    status["output"] = command.get_status()
    return status

@get("/download/<command_id>/<filename>")
def download(command_id, filename):
    if command_id not in commands:
        abort(404, '{"error": "Not found."}')
    command = commands[command_id]
    iso_path = command.get_iso_path()
    assert iso_path is not None
    return open(iso_path, "rb")


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