from unittest.mock import Mock
from pytest import fixture, raises
from codersos_image_server.build import Build

@fixture
def image():
    return Mock()

def pytest_generate_tests(metafunc):
    if 'commands' in metafunc.fixturenames:
        metafunc.parametrize("commands",
                             [[{"name": "test1", "command":"do1", "arguments": []},
                               {"name": "test2", "command":"do2", "arguments": ["2"]},
                               {"name": "test3", "command":"do3", "arguments": ["1", "2", "3"]}],
                              [{"name": "test1", "command":"doajshdkhkada", "arguments": ["asd", "-s", "asd"]},
                               {"name": "asd", "command":"asd", "arguments": ["1", "2"]}]])

@fixture
def build(image, commands):
    return Build(image, commands)
    

class TestStatus:

    def test_commands_are_all_listed(self, build, commands):
        status = build.get_status()
        assert len(status) == len(commands)
        for index, command in enumerate(commands):
            assert command["name"] == status[index]["name"]

    def test_commands_are_not_executed(self, build):
        for state in build.get_status():
            assert state["status"] == "waiting"

    def test_commands_are_executed(self, build):
        for run, state in enumerate(build.get_status()):
            build.execute_one_command()
            for index, state in enumerate(build.get_status()):
                if index <= run:
                    assert state["status"] == "stopped"
                else:
                    assert state["status"] == "waiting"

    def test_running_state(self, build, image, commands):
        i = 0
        def test(*args):
            nonlocal i
            command = commands[i]
            i += 1
            for status in build.get_status():
                assert (status["name"] == command["name"]) == (status["status"] == "running")
            return Mock()
        image.execute_file.side_effect = test
        build.execute()

    def test_return_code(self, build, image):
        build.execute_one_command()
        assert build.get_status()[0]["exitcode"] == image.execute_file.return_value.returncode


    def test_output(self, build, image):
        build.execute_one_command()
        assert build.get_status()[0]["output"] == image.execute_file.return_value.stdout.decode.return_value

    def test_build_without_commands_is_stopped(self):
        build = Build(Mock(), [])
        assert build.get_status_code() == "stopped"

class TestExecution:

    def test_execute_calls_all_commands(self, build, commands):
        build.execute_one_command = Mock()
        build.execute()
        assert build.execute_one_command.call_count == len(commands)

    def test_status_code(self, build, image, commands):
        def test(*args):
            assert build.get_status_code() == "running"
            return Mock()
        image.execute_file.side_effect = test
        for _ in commands:
            assert build.get_status_code() == "waiting"
            build.execute_one_command()
        assert build.get_status_code() == "stopped"

    def test_arguments_are_passed(self, build, commands, image):
        for i in range(len(commands)):
            build.execute_one_command()
            command = commands[i]
            image.execute_file.assert_called_with(command["command"], command["arguments"])

class TestISOPath:

    @fixture
    def stopped_build(self, build):
        build.get_status_code = lambda: "stopped"
        return build

    def test_get(self, stopped_build, image):
        assert stopped_build.get_iso_path() ==  image.get_file.return_value.name

    def test_no_path(self, stopped_build, image):
        def error(*args):
            raise FileNotFoundError()
        image.get_file = error
        assert stopped_build.get_iso_path() is None

    def test_get_file_with_iso_path(self, stopped_build, image):
        stopped_build.get_iso_path()
        image.execute_command.assert_called_once_with(["/toiso/iso_path.sh"])
        image.get_file.assert_called_once_with(image.execute_command.return_value.output.decode.return_value)

    def test_iso_path_checks_if_iso_could_be_read(self, stopped_build, image):
        stopped_build.get_iso_path()
        image.execute_command.return_value.check_returncode.assert_called_once_with()

    def test_only_from_stopped_build(self, build):
        with raises(AssertionError):
            build.get_iso_path()

    def test_iso_path_is_cached(self, stopped_build):
        stopped_build._get_iso_file = _get_iso_file = Mock()
        stopped_build.get_iso_path()
        stopped_build.get_iso_path()
        _get_iso_file.assert_called_once_with()

    def test_iso_path_comes_from_cache(self, stopped_build):
        stopped_build._get_iso_file = _get_iso_file = Mock()
        for i in range(4):
            assert stopped_build.get_iso_path() == _get_iso_file.return_value.name




