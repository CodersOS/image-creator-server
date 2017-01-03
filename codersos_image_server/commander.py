

class Commander:

    def __init__(self, base_image, commands):
        """Create a new Commander object that executes the commands on the base image.
        """
        self._image = self._create_image()
        self._status = []
        for command in commands:
            self._status.append({"name": command["name"], "status": "waiting"})
        self._index = iter(range(len(commands)))
        self._commands = commands

    def _create_image(self):
        """Create the image."""

    def get_status(self):
        """Returns the status based in the previous commands.
        """
        return self._status

    def get_iso_path(self):
        """Returns the path to the iso image.

        If there is no iso image, None is returned.
        """
        path = self._image.execute_command(["/toiso/iso_path.sh"]).output.decode()
        try:
            file = self._image.get_file(path)
        except FileNotFoundError:
            return None
        return file.name

    def execute(self):
        """Execute all commands."""
        for i in range(len(self._status)):
            self.execute_one_command()

    def execute_one_command(self):
        """Execute one command."""
        for index in self._index:
            status = self._status[index]
            status["status"] = "running"
            result = self._image.execute_file()
            status["status"] = "stopped"
            status["exitcode"] = result.returncode
            status["output"] = result.output.decode()
            break




