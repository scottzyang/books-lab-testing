import os
from unittest import TestCase

from datetime import date
 
from books_app.extensions import app, db, bcrypt
from books_app.models import Book, Author, User, Audience

"""
Run these tests with the command:
python -m unittest books_app.main.tests
"""

#################################################
# Setup
#################################################

def create_books():
    a1 = Author(name='Harper Lee')
    b1 = Book(
        title='To Kill a Mockingbird',
        publish_date=date(1960, 7, 11),
        author=a1
    )
    db.session.add(b1)

    a2 = Author(name='Sylvia Plath')
    b2 = Book(title='The Bell Jar', author=a2)
    db.session.add(b2)
    db.session.commit()

def create_user():
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):

        form_data = {
            'username': 'scottzyang',
            'password': 'thisismypassword'
        }
        self.app.post('/signup', data=form_data)
        # - Check that the user now exists in the database
        new_user = User.query.filter_by(username='scottzyang').one()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, 'scottzyang')

    def test_signup_existing_user(self):

        create_user()

        form_data = {
            'username': 'me1',
            'password': 'password'
        }
        response = self.app.post('/signup', data=form_data)
        response_data = response.get_data(as_text=True)

        self.assertIn('<li class="error">That username is taken. Please choose a different one.</li>', response_data)

    def test_login_correct_password(self):

        create_user()

        form_data = {
            'username': 'me1',
            'password': 'password'
        }

        response = self.app.post('/login', data=form_data)
        response_data = response.get_data(as_text=True)

        self.assertNotIn('<a href="/login">Log In</a>', response_data)

    def test_login_nonexistent_user(self):
        form_data = {
            'username': 'scottzyang',
            'password': 'asdfasdf'
        }

        response = self.app.post('/login', data=form_data)
        response_data = response.get_data(as_text=True)

        self.assertIn('<li class="error">No user with that username. Please try again.</li>', response_data)


    def test_login_incorrect_password(self):
        create_user()

        form_data = {
            'username': 'me1',
            'password': 'pazzword'
        }
        response = self.app.post('/login', data=form_data)
        response_data = response.get_data(as_text=True)

        self.assertIn('<li class="error">Password doesn&#39;t match. Please try again.</li>', response_data)

    def test_logout(self):
        create_user()
        
        form_data = {
            'username': 'me1',
            'password': 'password'
        }

        self.app.post('/login', data=form_data)
        response = self.app.get('/logout', follow_redirects=True)
        response_data = response.get_data(as_text=True)
  
        self.assertIn('<a href="/login">Log In</a>', response_data)

