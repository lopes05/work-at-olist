from django.core.management.base import BaseCommand, CommandError
from books_app.models import Author
import csv

class Command(BaseCommand):
    """
        Populate authors table with content coming from a CSV file
    """
    def add_arguments(self, parser):
        parser.add_argument("csv_entry", help="CSV file containing authors", type=open)
        
    def handle(self, *args, **options):
        self.stdout.write("Init Authors Creation")
        csv_file = options.get('csv_entry')
        try:
            csv_content = csv.DictReader(csv_file)
            batch = [Author(name=author_row['name'].strip()) for author_row in csv_content]
        except Exception as e:
            self.stderr.write("Error on document format.")
            return
        
        res = Author.objects.bulk_create(batch, ignore_conflicts=True)
        self.stdout.write("Finish authors creation")