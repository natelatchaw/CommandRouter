import pathlib
import pytest
from router.handler import Handler

class TestHandler:
    def test_handler_load_invalid_directory(self):
        """
        Test to see if loading an invalid path throws a TypeError
        """
        handler: Handler =  Handler()
        with pytest.raises(TypeError):
            handler.load('')

    def test_handler_load_empty_directory(self, tmp_path: pathlib.Path):
        """
        Check behavior on loading empty directory
        """
        # generate path for test component folder
        test_components: pathlib.Path = tmp_path.joinpath('test_components')
        # make the directory from the path
        test_components.mkdir(parents=True)
        # initialize Handler instance
        handler: Handler = Handler()
        # load the test component folder
        handler.load(test_components)