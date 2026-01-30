import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect
from service.controllers.ExampleController import ExampleController
from service.entities.ExampleEntity import ExampleEntityModel


class TestExampleController(unittest.TestCase):
    """
    Example test for the controller
    Works by mocking the database.
    """

    @classmethod
    def setUpClass(cls):
        connect('mongoenginetest', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
       disconnect()

    def test_add_entity(self):
        """
        Tests that the 'add_entity' method works.
        """
        # add entity to the controller
        controller = ExampleController()
        controller.add_entity({'post_name': 'some name', 'post_body': 'lorem_ipsum'})

        # test that the entity was added
        added_entity = ExampleEntityModel.objects().first()
        assert added_entity.post_name == 'some name'





