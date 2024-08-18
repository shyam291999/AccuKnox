from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from rest_framework.serializers import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
       
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=25, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    friends = models.ManyToManyField('self', through="Friendship", symmetrical=False )
    phone = models.CharField(max_length=10, unique=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)  
    is_staff = models.BooleanField(default=False)
    password = models.CharField(max_length=20)
   
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', "phone"]


    def validate_phone(value):

        if len(value) != 10:
            raise ValidationError(
                "Enter a valid mobile number. It should be between 10 digits"
            )
        if not value.is_digit():
             raise ValidationError(
                "Mobile number must contain digits only"
            )

    def __str__(self):
        return self.username
    
# superuser credentials
# Email: admin@gmail.com
# First name: admin
# Last name: admin
# Username: admin
# Phone: 9966339966
# Password: Auth@123


class Friendship(models.Model):

    from_user = models.ForeignKey(User, related_name='request_send', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='request_received', on_delete=models.CASCADE )
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')