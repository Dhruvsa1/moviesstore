from django.core.management.base import BaseCommand
from movies.models import Movie


class Command(BaseCommand):
    help = 'Add the four demonstration movies without replacing existing records.'

    def handle(self, *args, **options):
        for name, price, description, image in [
            ('Inception', 12, 'A mind-bending heist thriller.', 'inception.jpg'),
            ('Avatar', 13, 'A journey to a distant world and the battle for resources.', 'avatar.jpg'),
            ('The Dark Knight', 14, 'Gothams vigilante faces the Joker.', 'dark.jpg'),
            ('Titanic', 11, 'A love story set against the backdrop of the sinking Titanic.', 'titanic.jpg'),
        ]:
            Movie.objects.get_or_create(name=name, defaults={
                'price': price, 'description': description, 'image': 'movie_images/' + image,
            })
        self.stdout.write(self.style.SUCCESS('Movie catalog ready.'))
