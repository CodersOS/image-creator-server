from codersos_image_server.image import Image
from pytest import fixture, raises
import subprocess
from unittest.mock import Mock

def containers():
    """Return the docker containers."""
    return set(subprocess.check_output(["docker", "ps", "-aq"]).decode().splitlines())

def images():
    return set(subprocess.check_output(["docker", "images", "-aq"]).decode().splitlines())

@fixture
def image():
    image = Image("ubuntu")
    yield image
    image.delete()

class TestCreateImage:

    def test_can_create_image(self):
        Image("ubuntu")

    def test_cannot_create_invalid_image(self):
        with raises(ValueError):
            Image("asdhgjsagjfgakdsghfskdh")

    def test_can_not_create_container_of_deleted_image(self, image):
        image.delete()
        with raises(ValueError):
            image.create_container()

    def test_can_create_container(self, image):
        image.create_container()

    def test_creating_a_container_does_not_create_extra_images(self, image):
        images_before = images()
        image.create_container()
        images_after = images()
        assert images_before <= images_after
        assert len(images_before) == len(images_after) - 1

    def test_creating_an_image_creates_a_new_docker_image(self):
        images_before = images()
        image = Image("ubuntu")
        images_after = images()
        assert images_before < images_after
        assert len(images_after - images_before) == 1
        for docker_image in images_after - images_before:
            assert image.docker_image == docker_image

    def test_docker_image_exists(self, image):
        assert image.docker_image in images()

    def test_no_container_is_left(self):
        container_before = containers()
        Image("ubuntu")
        containers_after = containers()
        assert container_before == containers_after

class TestDeleteImage:

    def deleting_the_container_removes_docker_image(self, image):
        image_before = image.docker_image
        image.delete_container()
        assert image.docker_image is None
        assert image.docker_image not in images()


class TestExecuteACommand:

    def exec(self, image, command):
        return image.execute_command(command)

    def test_creates_new_image(self, image):
        image_before = image.docker_image
        self.exec(image, ["touch x"])
        image_after = image.docker_image
        assert image_before != image_after

    def test_can_not_delete_old_image(self, image):
        image_before = image.docker_image
        self.exec(image, ["touch x"])
        assert image_before in images()

    def test_no_container_is_left(self, image):
        container_before = containers()
        self.exec(image, "touch x")
        containers_after = containers()
        assert container_before == containers_after

    def test_output(self, image):
        string = "jahslfhawuehifdsjhawuhefhkdsjkfhawu"
        result = self.exec(image, ["echo", "-n", string])
        assert result.stdout.decode() == string

    def test_stdout_and_stderr_is_mixed(self, image):
        result = self.exec(image, ["bash", "-c", "echo 1 ; echo 2 1>&2 ; echo 3"])
        assert set(result.stdout.decode().splitlines()) == {"1", "2", "3"}

    def test_return_code_is_zero(self, image):
        result = self.exec(image, ["echo"])
        assert result.returncode == 0
        
    def test_return_code_is_nonzero(self, image):
        result = self.exec(image, ["bash", "-c", "exit 123"])
        assert result.returncode == 123
        

class TestDeleteImage:

    def test_del_calls_delete(self, image):
        image.delete = Mock()
        image.__del__()
        image.delete.assert_called_once_with()

    def test_container(self, image):
        image.delete_container = Mock()
        image.delete()
        image.delete_container.assert_called_once_with()

    def test_isos(self, image):
        image.delete_iso_files = Mock()
        image.delete()
        image.delete_iso_files.assert_called_once_with()

    def test_can_delete_image_twice(self, image):
        image.delete()
        image.delete()


class TestExecuteFile(TestExecuteACommand):

    def exec(self, image, command):
        file_content = "#!/bin/bash\n'" + "' '".join(command) + "'\n"
        return image.execute_file(file_content)


