from codersos_image_server import Image
from pytest import fixture
import subprocess

def containers():
    """Return the docker containers."""
    return set(subprocess.check_output("docker", "ps", "-aq").splitlines())

def images():
    return set(subprocess.check_output("docker", "images", "-aq").splitlines())

@fixture
def image():
    return Image("ubuntu")

class TestCreateImage:

    def test_can_create_image(self):
        Image("ubuntu")

    def test_cannot_create_invalid_image(self):
        Image("asdhgjsagjfgakdsghfskdh")

    def test_can_not_create_container_of_deleted_image(self, image):
        image.delete()
        assert raises(AssertionError):
            image.create_container()

    def test_can_create_container(self, image):
        image.create_container()

    def test_creating_a_container_does_not_create_extra_images(self, image):
        images_before = images()
        image.create_container()
        images_after = images()
        assert images_before == images_after

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

    def test_creates_new_image(self, image):
        image_before = image.docker_image
        image.execute_command(["ls"])
        image_after = image.docker_image
        assert image_before != image_after

    def test_delete_old_image(self, image):
        image_before = image.docker_image
        image.execute_command("ls")
        assert image_before not in images()

    def test_no_container_is_left(self, image):
        container_before = containers()
        image.execute_command("ls")
        containers_after = containers()
        assert container_before == containers_after

    def test_output(self, image):
        string = "jahslfhawuehifdsjhawuhefhkdsjkfhawu"
        result = image.execute_command(["echo", "-n", string])
        assert result.stdout == string

    def test_stdout_and_stderr_is_mixed(self, image):
        result = image.execute_command(["bash", "-c", "echo -n 1 ; echo -n 2 1>&2 ; echo -n 3"])
        assert result == "123"

    def test_return_code_is_zero(self, image):
        result = image.execute_command(["echo"])
        assert result.returncode == 0
        
    def test_return_code_is_nonzero(self, image):
        result = image.execute_command(["exit", "123"])
        assert result.returncode == 123
        











