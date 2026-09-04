from django.contrib import admin

from .models import Post

# Registering Post makes it manageable from /admin/ - add, edit, delete
# posts through Django's built-in admin site instead of the shell.
admin.site.register(Post)
