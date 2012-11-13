from django.core.management.base import NoArgsCommand

from django.contrib.auth.models import User


class Command(NoArgsCommand):
    help = "Create an admin user if it doesn't already exist"

    def handle_noargs(self, **options):
        u, created = User.objects.get_or_create(username='admin')
        password = 'P@s$w0rd1'
        if created:
            u.set_password(password)
            u.is_superuser = True
            u.is_staff = True
            u.save()
            print("admin user has been created with a password of '%s', " \
                   "please login to admin and change right away." % password)
        else:
            print("admin user already created.")

# once done, login immediately and change the password to something more secure.