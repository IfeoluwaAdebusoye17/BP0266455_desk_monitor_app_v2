import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()
database_uri = os.getenv('SQL_DATABASE_URI')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class TestSQLInjection(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        # Create a test table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name TEXT
            )
        """))
        db.session.commit()

    
    def tearDown(self):
        # Drop the test table
        db.session.execute(text("DROP TABLE IF EXISTS test_table"))
        db.session.commit()
        self.app_context.pop()
    
    def test_sql_injection(self):
        # Attempt to perform SQL injection
        malicious_input = "'; DROP TABLE test_table; --"
        try:
            db.session.execute(text("INSERT INTO test_table (name) VALUES (:name)"), {'name': malicious_input})
            db.session.commit()
        except Exception as e:
            self.assertIn("syntax error", str(e))

        # Verify the table still exists
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name='test_table'"))
        tables = result.fetchall()
        self.assertTrue(len(tables) > 0, "SQL injection failed, table still exists")

