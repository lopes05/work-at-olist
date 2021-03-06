from django.test import TestCase, Client
from rest_framework.test import APIClient


from library_project.settings import REST_FRAMEWORK as drf_configs
from books_app.models import Author
import json
# Create your tests here.

class AuthorViewsTest(TestCase):

    client = APIClient()

    AUTHORS = [
        'Mário de Andrade',
        'Clarice Linspector',
        'Carlos Drummond de Andrade',
        'Guimarães Rosa',
        'William Shakespeare',
        'Jorge Amado',
        'Graciliano Ramos',
        'J.K. Rowling',
        'José de Alencar',
        'Cecília Meireles',
        'Monteiro Lobato',
        'Vinicius de Moraes',
        'José Saramago'
    ]

    def setUp(self):
        """
            Setting up test database
        """
        authors = [Author(name=name) for name in self.AUTHORS]
        Author.objects.bulk_create(authors, ignore_conflicts=True)

    def test_list_authors_response_ok(self):
        """
            Test listing all authors endpoint
        """
        response = self.client.get("/authors/")
        self.assertEquals(response.status_code, 200)
    
    def test_list_all_authors_json_content(self):
        """
            Test GET (list) authors response content
        """
        response = self.client.get("/authors/")
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content['count'], Author.objects.all().count())
        self.assertEquals(sorted(content['results'][0].keys()), sorted(['id', 'name']))

    def test_list_all_authors_pagination(self):
        """
            Test first page retrieving all results possible for one page size, full page of authors
        """
        if len(self.AUTHORS) < drf_configs["PAGE_SIZE"]:
            Author.objects.bulk_create((Author(name=f"author{x}") for x in range(drf_configs["PAGE_SIZE"]-len(self.AUTHORS))))
        response = self.client.get("/authors/?page=1")
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(len(content['results']), drf_configs['PAGE_SIZE'])

    def test_list_all_authors_page_with_less_results(self):
        """
            Test page with less than the page limit size
        """
        if len(self.AUTHORS) < drf_configs["PAGE_SIZE"]:
            Author.objects.bulk_create((Author(name=f"author{x}") for x in range(drf_configs["PAGE_SIZE"]+1)))
        response = self.client.get("/authors/?page=2")

        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(len(content['results']) < drf_configs['PAGE_SIZE'])
    
    def test_search_authors_by_exact_name(self):
        """
            Test the name filtering in authors request with full name
        """
        response = self.client.get(f"/authors/?name={self.AUTHORS[2]}")
        self.assertEquals(response.status_code, 200)
        # should get only one Author
        content = json.loads(response.content)
        self.assertEquals(len(content['results']), 1)

    def test_search_authors_containing_query(self):
        """
            Test the name filtering in authors request, need to retrieve more than one content,
            if substring is present in more than one name
        """
        response = self.client.get(f"/authors/?name=José")
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        # should get two authors which names contains the letter 'c'
        self.assertEquals(len(content['results']), 2)

    def test_search_authors_retrieves_nothing(self):
        """
            Test GET request returns empty list when filtering a name
        """
        response = self.client.get(f"/authors/?name=Gustavo")
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(len(content['results']), 0)
    
    def test_get_author(self):
        """
            Test specific author content
        """
        response = self.client.get(f"/authors/1/")
        self.assertEquals(response.status_code, 200)
        # should get the first author in thist test database list
        content = json.loads(response.content)
        self.assertEquals(content['name'], self.AUTHORS[0])

    def test_get_author_fails(self):
        """
            Test not to retrieve an author, when invalid id is passed
        """
        response = self.client.get(f"/authors/20/")
        # there is no author with id 10, should fail
        self.assertEquals(response.status_code, 404)
        