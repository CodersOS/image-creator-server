from subprocess import run, STDOUT
from tempfile import NamedTemporaryFile


def docker(*args, **kw):
    """Run a docker command."""
    kw.setdefault("check", True)
    return run(("docker", ) + args, check=check, **kw)


class Image(object):

    def __init__(self, base_docker_image):
        """Create a new image based on the base_docker_image.
        """
        self._image = base_docker_image
        self._has_container = False
        self.create_container()

    def create_container(self):
        """This creates the container based on the base_docker_image.

        This container is used to issue commands.
        """
        container = docker("create", self._image)
        self._image = docker("commit", container).stdout
        docker("rm", container)
        self._has_container = True

    def delete_container(self):
        """Delete the container and the corresponding container image.

        This can only be executed after create_container() is executed.
        """
        assert self._has_container
        docker("rmi", self._image)

    def execute_command(self, command):
        """Execute a command in the container.

        The command is executed on the command line.
        Example:

            execute_command(["ls", "/"])

        :return: The exit code and stdout.
        :rtype: subprocess.CompletedProcess

        You can only execute one command at a time!
        """
        assert self._has_container
        with NamedtemporaryFile() as container_id_file:
            result = docker("run", "--cidfile", container_id_file.name, self._image, *command, stderr=STDOUT, check=False)
            container_id = container_id_file.read()

    def execute_file(self, content, arguments=()):
        """Execute a file with a certain content.

        The content of the file is added to `/tmp/command`.
        Then, the file is executed.
        Example:

               execute_file("#!/bin/bash\nls $1\n", "/")
            -> /tmp/command /
            -> ls /

        :return: The exit code of the command.
        :rtype: int

        You can only execute one command at a time!
        """
        assert self._has_container

    def create_iso_file(self):
        """Create the live image in an iso format.

        :return: The path to the iso file.
        :rtype: str
        """
        assert self._has_container

    def delete_iso_files(self):
        """Delete all iso files."""

    def delete(self):
        """When this object is deleted, iso and containers are deleted.

        This deletes the container and the iso files.
        """

    __del__ = delete