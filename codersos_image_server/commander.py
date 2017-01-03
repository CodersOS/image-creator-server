

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
        self._status_code = "waiting"

    def _create_image(self):
        """Create the image."""
        # TODO: create correct image

    def get_status(self):
        """Returns the status based in the previous commands.
        """
        return self._status

    def get_status_code(self):
        """Return either "waiting" or "running" or "stopped"."""
        return self._status_code

    def get_iso_path(self):
        """Returns the path to the iso image.

        If there is no iso image, None is returned.
        """
        result = self._image.execute_command(["/toiso/iso_path.sh"])
        result.check_returncode()
        path = result.output.decode() # TODO: checkresult
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
        stopped = True
        for index in self._index:
            self._status_code = "running"
            try:
                status = self._status[index]
                status["status"] = "running"
                command = self._commands[index]
                result = self._image.execute_file(command["command"], command["arguments"])
                status["status"] = "stopped"
                status["exitcode"] = result.returncode
                status["output"] = result.output.decode()
            finally:
                self._status_code = ("stopped" if index == len(self._commands) - 1 else "waiting")
            break





