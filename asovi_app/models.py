from django.db.models.deletion import CASCADE, get_candidate_relations_to_delete
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
import re, random, string


class CustomUserManager(UserManager):
    use_in_migrations = True

    def get_user_id(self, num):
        # <num>文字のランダムな文字列を生成
        return ''.join(random.choices(string.ascii_letters + string.digits, k=num))

    def _create_user(self, email, password, user_id, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        def isHalf(value):
            """
            半角文字(半角カナ以外）かチェック
            user_idが全て半角文字の場合、True
            """
            return re.match(r"^[\x20-\x7E]+$", value) is not None

        user = self.model(email=email, user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        extra_fields.setdefault('user_id', self.get_user_id(10))
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    user_id = models.CharField(_('user id'), max_length=50, blank=False, unique=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        )
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designate whether this user should be treated as active.'
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, selef.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        return self.email


class Genre(models.Model):
    name = models.CharField(max_length=60)

    class Meta:
        verbose_name_plural = 'genre'

    def __str__(self):
        return self.name


class Profile(models.Model):

    GENDER_CHOICES = [
        (1,'男'),
        (2,'女'),
        (3,'その他'),
    ]

    user = models.OneToOneField(CustomUser,related_name="user_profile",on_delete=CASCADE)
    username = models.CharField(max_length=50)
    icon = models.ImageField(upload_to="static/img/",null=True,blank=True)
    introduction = models.TextField(null=True,blank=True)
    interested_genre = models.ManyToManyField(Genre)
    gender = models.IntegerField(choices=GENDER_CHOICES,default=0,null=True,blank=True)

    class Meta:
        verbose_name_plural = 'Profile'

    def __str__(self):
        return '<UserProfile:userid=' + str(self.user.id) + ',username=' + self.username + '>'


# Create y
class post(models.Model):
    image=models.ImageField(upload_to="images")
    time=models.DateTimeField(null=True)
    body=models.CharField(max_length=300,unique=True)
    latitude=models.FloatField(null=True,blank=True)
    longitude=models.FloatField(null=True,blank=True)
