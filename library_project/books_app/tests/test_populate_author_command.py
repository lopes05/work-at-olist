from django.test import TestCase, Client
from rest_framework.test import APIClient

from django.core.management import call_command
from books_app.models import Author
import json
from io import StringIO
# Create your tests here.

class PopulateAuthorCommandTest(TestCase):
    
    def test_command_output_invalid_file(self):
        """
            Test if the command fails, when an invalid file is provided.
        """
        out = StringIO()
        err_out = StringIO()
        call_command('populate_authors', 'books_app/tests/fixtures/invalid_authors.csv', stdout=out,stderr=err_out)
        self.assertIn('Init Authors Creation', out.getvalue())
        self.assertIn('Error on document format.', err_out.getvalue())

    def test_command_valid_file(self):
        """
            Test if the command is populating the database and outputting the correct message
        """
        out = StringIO()
        err_out = StringIO()
        call_command('populate_authors', 'books_app/tests/fixtures/authors.csv', stdout=out,stderr=err_out)
        self.assertIn('Init Authors Creation', out.getvalue())
        self.assertNotIn('Error on document format.', err_out.getvalue())
        self.assertIn('Finish authors creation', out.getvalue())
        authors = Author.objects.all()
        with open('books_app/tests/fixtures/authors.csv') as f:
            lines = list(f)
        self.assertEquals(authors.count(), len(lines) - 1)

    def test_command_valid_file_with_duplicate(self):
        """
            Test the ignore_conflicts param in bulk_create when trying to create authors with 
            duplicated names
        """
        out = StringIO()
        err_out = StringIO()
        Author.objects.create(name="test1")
        call_command('populate_authors', 'books_app/tests/fixtures/authors.csv', stdout=out,stderr=err_out)
        self.assertIn('Init Authors Creation', out.getvalue())
        self.assertNotIn('Error on document format.', err_out.getvalue())
        self.assertIn('Finish authors creation', out.getvalue())
        authors = Author.objects.all()
        with open('books_app/tests/fixtures/authors.csv') as f:
            lines = list(f)
        self.assertEquals(authors.filter(name="test1").count(), 1)
        self.assertEquals(authors.count(), len(lines) - 1)

    