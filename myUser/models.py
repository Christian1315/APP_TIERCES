from django.db import models

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, AbstractUser

from django.contrib.auth.base_user import BaseUserManager


class MyUserManager(BaseUserManager):
    def _create_user(self, username, password, **extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        user = self.model(
            username=username,
            password=password,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username,password, **extra_fields):
        return self._create_user(username,password,**extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self._create_user(username, password, **extra_fields)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MyUser(AbstractUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    is_DeliveryMan = models.BooleanField(default=False) 
    is_RelayPoint = models.BooleanField(default=False) 

    objects = MyUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["password"]
