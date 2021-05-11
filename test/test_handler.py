import pytest
from ..router.handler import Handler

class TestHandler:
    def test_handler(self):
        """
        Test to see if loading an invalid path throws a TypeError
        """
        handler: Handler =  Handler()
        with pytest.raises(TypeError):
            handler.load('')