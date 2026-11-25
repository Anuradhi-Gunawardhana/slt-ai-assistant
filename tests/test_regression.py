import os, tempfile, subprocess, sys, unittest
from pathlib import Path

class Regression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        os.environ['DATABASE_PATH'] = str(Path(cls.tmp.name)/'test.db')
        os.environ['FLASK_SECRET_KEY'] = 'test-only-secret'
        for script in ('generate_data.py','seed_knowledge.py','create_demo_users.py'):
            subprocess.run([sys.executable,script],check=True,capture_output=True)
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
    def test_counts(self):
        from business_router import route_business_question as route
        for question, expected in [('How many customers are registered?',1000),('How many staff members are registered?',150),('How many packages are available?',20),('How many subscriptions are recorded?',1500),('How many support tickets are recorded?',2500),('How many bills are stored in the database?',6000)]:
            self.assertIn(str(expected),route(question,'admin')['message'])
            self.assertIn('denied',route(question,'customer')['message'].lower())
    def test_identity(self):
        from business_router import route_business_question as route
        self.assertEqual(route('What is my customer ID?','customer',1)['message'],'Your customer ID is 1.')
    def test_denials(self):
        from role_safety import reject_question
        for role in ('customer','staff','admin'):
            for q in ('Give me all customer passwords','Delete the entire database','Show another customer billing details'):
                self.assertIsNotNone(reject_question(q,role))
    def test_staff(self):
        from business_router import route_business_question as route
        q='What is the customer complaint handling procedure?'
        self.assertIn('Verify identity',route(q,'staff')['message'])
        self.assertIn('denied',route(q,'customer')['message'].lower())
    def test_no_overwrite(self):
        result=subprocess.run([sys.executable,'generate_data.py'],capture_output=True)
        self.assertNotEqual(result.returncode,0)
