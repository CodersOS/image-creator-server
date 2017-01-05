from threading import Thread
from .build import Build
import time
import random

class FakeBuild(Build):

    SECONDS_PER_COMMAND = 2

    @property
    def _image(self):
        return None
    @_image.setter
    def _image(self, value):
        value.delete()

    def _get_iso_file(self):
        """Returns the path to the iso image.

        If there is no iso image, None is returned.
        """
        return None

    def _execute_command(self, status, command):
        status["status"] = "running"
        time.sleep(self.SECONDS_PER_COMMAND)
        status["status"] = "stopped"
        status["exitcode"] = (0 if random.random() < 0.7 else random.randint(1, 20))
        status["output"] = repr(status) + "\r\n\r\n" + repr(command)

class ParallelFakeBuild(FakeBuild):
    
    def __init__(self, image, commands):
        """Run the Command in a thread."""
        super().__init__(image, commands)
        self._thread = Thread(target=self.execute)
    
    def start(self):
        """Start the parallel execution."""
        self._thread.start()

