image-creator-server Documentation
==================================


Configuration
-------------

You can configure the following locally:

- the base image to use:
  
        "base_image" : "codersos/linux-image-creator"

API
---

- **POST /create**  
  Post a json in the following format:

        {
          "redirect" : "REDIECT-URL",
          "commands" : [
            {
              "name" : "COMMAND-NAME",
              "command" : "COMMAND",
              "arguments" : ["ARGUMENT", ...]
            },
            ...
          ]
        }
    
  These have the following meaning:
  
  - `redirect` must be given. `REDIRECT-URL` is the url where the user
    gets redirected to once the build started. It gets an additional argument
    `status` which is appended like this:
     - `http://asd.asd/x/` becomes
       `http://asd.asd/x/?status=STATUSURL`
     - `http://asd.asd/x?asd=asd` becomes
       `http://asd.asd/x?asd=asd&status=STATUSURL`
    This is done leaving as much intact as possible.
    `STATUSURL` is replaced with the url of the build status,
    see **GET /status/ID**.
  - `commands` is a list of commands that should be executed on the
    linux image.
    For each command in the list, the `name` attribute MUST be given.
    Also, either the `url` or the `command` attribute MUST be given.
    - `COMMAND-NAME` is the name of the command for identification.
      Example: `Install Firefox`
    - `COMMAND` is the command to execute. It gets saved to
      `/tmp/command`, is made executable and is executed.
      Examples:
      - ```
        #!/bin/bash
        wget http://some.docu/ment.txt -O /home/ubuntu/
        ```
      - ```
        #!/usr/bin/python
        # doing some python stuff
        ```
    - `ARGUMENT` is part of a list of arguments to the `COMMAND` file.
    - `arguments` must be given.

- **GET /status/ID**  
  The result of this GET request is a JSON like this:
  ```
  {
    "status" : "STATUS-CODE",
    "commands" : [
      {
        "name" : "COMMAND-NAME",
        "output" : "COMMAND-OUTPUT",
        "status" : "STATUS-CODE"
      },
      ...
    ],
    "exitcode" : EXIT-CODE,
    "download" : "DOWNLOAD-URL"
  }
  ```
  The parts have the following meaning:
  - `STATUS-CODE` is one of the following:
    - `waiting` - if the process is not yet started
    - `running` - if the process is currently runnning
    - `stopped` - if the process succeeded
  - `commands` are a list of commands.
    All of the commands in the **POST /create** MUST be present.
    There MAY be additional commands.
    - `COMMAND-NAME`, see above, the name of a command.
    - `COMMAND-OUTPUT` - the stdout and stderr combined string of command
      output. This is useful for debugging.
      Commands with status `stopped` must have the `output` attribute.
  - `DOWNLOAD-URL` is the URL where the result can be downloaded once the
    process exited with `STATUS-CODE` `stopped`.
    If `exitcode` is 0, then the url MUST be present.

- **GET /source**  
  The result is a zip file with the current source code.