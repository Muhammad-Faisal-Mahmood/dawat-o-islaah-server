from django.contrib import admin
from .models import User
# Register your models here.
class admin_user(admin.ModelAdmin):
    model=User
admin.site.register(User,admin_user)