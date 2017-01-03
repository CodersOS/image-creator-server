import os

from shutil import rmtree
from subprocess import run, STDOUT, PIPE, CalledProcessError
from tempfile import mkdtemp, NamedTemporaryFile
from contextlib import contextmanager


def docker(*args, **kw):
    """Run a docker command."""
    kw.setdefault("check", True)
    kw.setdefault("stdout", PIPE)
    kw.setdefault("stderr", PIPE)
    return run(("docker", ) + args, **kw)

def docker_id(process):
    """Return the docker id from the process output."""
    return process.stdout.decode().strip()

class Image(object):

    def __init__(self, base_docker_image):
        """Create a new image based on the base_docker_image.
        """
        self._image = base_docker_image
        self.create_container()

    def copy(self):
        """Create a copy of this image."""
        copy = self.__class__(self._image)
        self.create_container()
        return copy

    @property
    def docker_image(self):
        """The id of the current docker image."""
        if self._image.startswith("sha256:"):
            return self._image[7:19]
        return self._image

    def create_container(self):
        """This creates the container based on the docker_image.

        This container is used to issue commands.
        """
        with self._create_container():
            pass

    def __create_container(self):
        """This creates the container based on the base_docker_image.

        This container is used to issue commands.
        """
        if not self.has_docker_image():
            raise ValueError("Image {} not found.".format(self._image))
        try:
            container_id = docker_id(docker("create", self._image))
        except CalledProcessError:
            raise ValueError("Image {} not found.".format(self._image))
        yield container_id
        self.__use_container_image(container_id)

    def __use_container_image(self, container_id):
        self._image = docker_id(docker("commit", container_id))
        docker("rm", container_id)

    def _create_container(self):
        """This creates the container based on the docker_image.

        This container is used to issue commands.
        Use is like this:

            with self._create_container() as container_id:
                 # do something with the container
            # the container is destroyed and the current image is in the container.
        """
        return contextmanager(self.__create_container)()

    def delete_container(self):
        """Delete the container and the corresponding container image.

        This can only be executed after create_container() is executed.
        """
        if self.has_docker_image():
            docker("rmi", self._image)
            self._image = None

    def has_docker_image(self):
        """Whether the Image has a docker image."""
        return self._image is not None

    def execute_command(self, command, input=None):
        """Execute a command in the container.

        The command is executed on the command line.
        Example:

            execute_command(["ls", "/"])

        :return: The exit code and stdout.
        :rtype: subprocess.CompletedProcess

        You can only execute one command at a time!
        """
        assert self.has_docker_image()
        temporary_directory = mkdtemp()
        try:
            container_id_file_name = os.path.join(temporary_directory, "id")
            result = docker("run", "--cidfile", container_id_file_name, self._image, *command,
                            stderr=STDOUT, check=False, input=input)
            with open(container_id_file_name) as container_id_file:
                container_id = container_id_file.read()
            self.__use_container_image(container_id)
            return result
        finally:
            rmtree(temporary_directory)

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
        self.add_file("/tmp/command", content)
        self.execute_command(["chmod", "+x", "/tmp/command"]).check_returncode()
        return self.execute_command(["/tmp/command"] + list(arguments))

    def add_file(self, path, content):
        """Add a file to the image."""
        self.execute_command(["mkdir", "-p", os.path.dirname(path)])
        if isinstance(content, bytes):
            file = NamedTemporaryFile("wb")
        else:
            file = NamedTemporaryFile("w")
        with file:
            file.write(content)
            file.flush()
            with self._create_container() as container_id:
                docker("cp", file.name, container_id + ":" + path).check_returncode()

    def get_file(self, path, binary=True):
        """Return a file object with the copied content of the file in the container.

        This returns a TemporaryFile with the content of the file from the file system.
        If the file does not exists, an FileNotFoundError is raised.
        """
        assert isinstance(binary, bool)
        mode = ("rb" if binary else "r")
        file = NamedTemporaryFile(mode)
        file.file.close()
        with self._create_container() as container_id:
            result = docker("cp", container_id + ":" + path, file.name, check=False)
        if result.returncode != 0:
            raise FileNotFoundError(path, result)        
        file.file = open(file.name, mode)
        return file

    def delete(self):
        """When this object is deleted, iso and containers are deleted.

        This deletes the container and the iso files.
        """
        self.delete_container()

    def __del__(self):
        """Delete everything when the image is garbage-collected."""
        self.delete()
