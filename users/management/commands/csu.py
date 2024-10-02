from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        superuser = User.objects.create(
            email='admin@admin.ru',
            first_name='Julya',
            last_name='Shapaeva',
            is_staff=True,
            is_superuser=True
        )

        superuser.set_password('mila8625')
        superuser.save()
