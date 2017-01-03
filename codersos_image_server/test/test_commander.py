from unittest.mock import Mock
from pytest import fixture
from codersos_image_server.commander import Commander

@fixture
def image():
    return Mock()

def pytest_generate_tests(metafunc):
    if 'commands' in metafunc.fixturenames:
        metafunc.parametrize("commands",
                             [[{"name": "test1", "command":"do1"}, {"name": "test2", "command":"do2"}, {"name": "test3", "command":"do3"}],
                              [{"name": "test1", "command":"doajshdkhkada"}, {"name": "asd", "command":"asd"}]])

@fixture
def commander(image, commands):
    class TestCommander(Commander):

        def _create_image(self):
            return image
    return TestCommander("base-image", commands)
    

class TestStatus:

    def test_commands_are_all_listed(self, commander, commands):
        status = commander.get_status()
        assert len(status) == len(commands)
        for index, command in enumerate(commands):
            assert command["name"] == status[index]["name"]

    def test_commands_are_not_executed(self, commander):
        for state in commander.get_status():
            assert state["status"] == "waiting"

    def test_commands_are_executed(self, commander):
        for run, state in enumerate(commander.get_status()):
            commander.execute_one_command()
            for index, state in enumerate(commander.get_status()):
                if index <= run:
                    assert state["status"] == "stopped"
                else:
                    assert state["status"] == "waiting"

    def test_running_state(self, commander, image, commands):
        i = 0
        def test(*args):
            nonlocal i
            command = commands[i]
            i += 1
            for status in commander.get_status():
                assert (status["name"] == command["name"]) == (status["status"] == "running")
            return Mock()
        image.execute_file = test
        commander.execute()

    def test_return_code(self, commander, image):
        commander.execute_one_command()
        assert commander.get_status()[0]["exitcode"] == image.execute_file.return_value.returncode


    def test_output(self, commander, image):
        commander.execute_one_command()
        assert commander.get_status()[0]["output"] == image.execute_file.return_value.output.decode.return_value

class TestExecution:

    def test_execute_calls_all_commands(self, commander, commands):
        commander.execute_one_command = Mock()
        commander.execute()
        assert commander.execute_one_command.call_count == len(commands)

class TestISOPath:

    def test_get(self, commander, image):
        assert commander.get_iso_path() ==  image.get_file.return_value.name

    def test_no_path(self, commander, image):
        def error(*args):
            raise FileNotFoundError()
        image.get_file = error
        assert commander.get_iso_path() is None

    def test_get_file_with_iso_path(self, commander, image):
        commander.get_iso_path()
        image.execute_command.assert_called_once_with(["/toiso/iso_path.sh"])
        image.get_file.assert_called_once_with(image.execute_command.return_value.output.decode.return_value)



