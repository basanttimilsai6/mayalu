from django.contrib import admin
from userprofile.models import User, UserProfile,Hobby

# Customize the UserProfile model display in the admin interface
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Hobby)
