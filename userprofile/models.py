from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, country_code, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field is required."))
        email = self.normalize_email(email)
        user = self.model(email=email, country_code=country_code, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, country_code, password=None, **extra_fields):
        """
        Create and return a superuser with an email, country_code, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, country_code, password, **extra_fields)

# Custom User Model
class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100,null=True, blank=True)
    password = models.CharField(max_length=100,null=True, blank=True)
    country_code = models.CharField(max_length=5)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["country_code"]

    def __str__(self):
        return self.email
    

    def save(self, *args, **kwargs):
        # Automatically generate username by taking the first 5 characters of the email
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)

class Hobby(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Other")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=100)
    hobbies = models.ManyToManyField(
        'Hobby', 
        blank=True, 
        related_name='user_profiles'
    )
    address = models.TextField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    nickname = models.CharField(max_length=50)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)

    # Additional fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # New field for phone number
    date_of_birth = models.DateField(null=True, blank=True)  # New field for date of birth
    social_media_links = models.JSONField(blank=True, null=True)  # New field for social media links (store in JSON)

    def __str__(self):
        return self.user.email
