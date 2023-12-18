import unittest
from main import User, create_app 
#from flask import json
import json
class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'
        }
        self.app, self.db = create_app(test_config)
        self.client = self.app.test_client()
        with self.app.app_context():
            self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def test_create_user(self):
        response = self.client.post('/user', data=json.dumps(dict(name='Test User')), content_type='application/json')
        self.assertNotEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()
