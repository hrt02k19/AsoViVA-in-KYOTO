from django.db.models.deletion import CASCADE, SET_NULL, get_candidate_relations_to_delete
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
import re, random, string


class CustomUserManager(UserManager):
    use_in_migrations = True

    def generate_user_id(self, num):
        # <num>文字のランダムな文字列を生成
        return ''.join(random.choices(string.ascii_letters + string.digits, k=num))


    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        def isHalf(value):
            """
            半角文字(半角カナ以外）かチェック
            user_idが全て半角文字の場合、True
            """
            return re.match(r"^[\x20-\x7E]+$", value) is not None

        user = self.model(email=email, **extra_fields)
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

        extra_fields.setdefault('user_id', self.generate_user_id(10))
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    user_id = models.CharField(_('user id'), max_length=50, unique=True)

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

    def isHalf(value):
        """
        半角文字(半角カナ以外）かチェック
        user_idが全て半角文字の場合、True
        """
        return re.match(r"^[\x20-\x7E]+$", value) is not None

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
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
    username = models.CharField(verbose_name='ユーザーネーム',max_length=50)
    icon = models.ImageField(verbose_name='アイコン',upload_to="static/asovi_app/img/",null=True,blank=True)
    introduction = models.TextField(verbose_name='紹介文',null=True,blank=True)
    interested_genre = models.ManyToManyField(Genre,verbose_name='興味のあるジャンル',blank=True)
    gender = models.IntegerField(verbose_name='性別',choices=GENDER_CHOICES,default=0,null=True,blank=True)

    class Meta:
        verbose_name_plural = 'Profile'

    def __str__(self):
        return '<UserProfile:userid=' + str(self.user.id) + ',username=' + self.username + '>'

class NotificationSetting(models.Model):
    user = models.OneToOneField(CustomUser,related_name="user_notification",on_delete=CASCADE)
    good = models.BooleanField(verbose_name='通知設定:いいね',default=True)
    has_saved = models.BooleanField(verbose_name='通知設定:保存',default=True)
    reply = models.BooleanField(verbose_name='通知設定:返信',default=True)
    friend = models.BooleanField(verbose_name='通知設定:フレンドリクエスト',default=True)

    class Meta:
        verbose_name_plural = '通知設定'

# Create y
class Post(models.Model):
    posted_by=models.ForeignKey(CustomUser,related_name='posted_by',on_delete=SET_NULL,null=True)
    image=models.ImageField(upload_to="static/asovi_app/img")
    genre=models.ForeignKey(Genre,related_name='post_genre',on_delete=SET_NULL,null=True,blank=True)
    time=models.DateTimeField(auto_now_add=True,null=True)
    body=models.TextField(max_length=300)
    latitude=models.FloatField(default=0)
    longitude=models.FloatField(default=0)
    place_id = models.CharField(max_length=100,null=True)
    like=models.IntegerField(default=0)
    place_id=models.TextField(null=True)
    place_name=models.TextField(null=True,blank=True)

class Save(models.Model):
    item = models.ForeignKey(Post,on_delete=models.CASCADE)
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)

class Good(models.Model):
    article = models.ForeignKey(Post,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    good = models.BooleanField(default=False)
    pub_date = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)

class Reply(models.Model):
    post = models.ForeignKey(Post,related_name="post_reply",on_delete=CASCADE)
    posted_by = models.ForeignKey(CustomUser,related_name="user_reply",null=True,on_delete=SET_NULL)
    body = models.TextField(max_length=300)
    pub_date = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)

class Friend(models.Model):
    requestor = models.ForeignKey(CustomUser, related_name='requestor', on_delete=CASCADE)
    requestee = models.ForeignKey(CustomUser, related_name='requestee', on_delete=CASCADE)
    friended = models.BooleanField(default=False)
    requested_date = models.DateTimeField(auto_now_add=True)
    friended_date = models.DateTimeField(blank=True, null=True)
    request_checked = models.BooleanField(default=False)

class Block(models.Model):
    blocker = models.ForeignKey(CustomUser,related_name="blocker",on_delete=CASCADE)
    blocked = models.ForeignKey(CustomUser,related_name="blocked",on_delete=CASCADE)
    block_date = models.DateTimeField(auto_now=True)

class Contact(models.Model):
    contacter=models.ForeignKey(CustomUser,on_delete=CASCADE)
    content=models.TextField(null=False,max_length=500)


class Popular(models.Model):
    num=models.IntegerField()
    place_name=models.TextField(null=True)