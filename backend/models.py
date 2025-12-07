from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        user = self.create_user(username, password, **extra_fields)
        
        admin_group, created = Group.objects.get_or_create(name="Admin")
        user.groups.add(admin_group)
        
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    role = models.CharField(
        max_length=20,
        choices=(
            ("админ", "админ"),
            ("заведующий", "заведующий"),
        ),
        default="заведующий",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    branches = models.ManyToManyField(
        "Branch",
        related_name="heads",
        blank=True
    )

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user.",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'Пользователь (Заведующий)'
        verbose_name_plural = 'Пользователи (Заведующии)'


class SurgeryType(models.Model):
    type_name = models.CharField(max_length=255, verbose_name='Название типа oперация', unique=True)

    class Meta:
        verbose_name = 'Тип операции (Примечания)'
        verbose_name_plural = 'Тип операции (Примечания)'

    def __str__(self):
        return self.type_name


class SurgeryName(models.Model):
    surgery_name = models.CharField(max_length=255, verbose_name='Название oперация', unique=True)

    class Meta:
        verbose_name = 'Название операции'
        verbose_name_plural = 'Название операции'
    
    def __str__(self):
        return self.surgery_name


class Surgeon(models.Model):
    full_name = models.CharField(unique=True, max_length=255, verbose_name='Ф.И.О Хирурга')
    branch = models.ManyToManyField(to="Branch", related_name="surgeons",  verbose_name="Отделении")

    class Meta:
        verbose_name = 'Хирург'
        verbose_name_plural = 'Хирурги'
    
    def __str__(self):
        return self.full_name


class Branch(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название отдела')

    branch_choices = [(i, str(i)) for i in range(1, 20)]
    branch_number = models.IntegerField(verbose_name='Номер отдела', choices=branch_choices)
    page_number = models.IntegerField(verbose_name='Номер страницы', default=1)

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отдели'
    
    def __str__(self):
        return f'Оп №{self.branch_number} | ' + self.name


class Surgery(models.Model):
    seq_number = models.PositiveIntegerField(default=0)
    branch = models.ForeignKey(to=Branch, on_delete=models.CASCADE, related_name='surgeries', verbose_name='Oтдел')
    own_branch = models.ForeignKey(to=Branch, on_delete=models.CASCADE, related_name='own_branchs_surgeries', verbose_name="Древний Oтдел")
    full_name = models.CharField('Ф.И.О пациента', max_length=255)
    age = models.IntegerField(verbose_name='Возраст', null=True, blank=True)
    diagnost = models.CharField(verbose_name='Диагноз', max_length=255)
    surgery_name = models.ForeignKey(to=SurgeryName, on_delete=models.CASCADE, related_name='surgeries')
    surgery_type = models.ForeignKey(to=SurgeryType, on_delete=models.CASCADE, related_name='surgeries', null=True, blank=True)
    surgeons1 = models.ManyToManyField(to=Surgeon, related_name='surgerie')
    surgeons = models.ManyToManyField(to=Surgeon, related_name='surgeries', through='SurgerySurgeon')
    date_of_surgery = models.ForeignKey(to='SurgeryDay', on_delete=models.CASCADE, related_name='surgeries', verbose_name='Дата операции', null=True)

    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'

    def __str__(self):
        return self.surgery_name.surgery_name


class SurgerySurgeon(models.Model):
    surgery = models.ForeignKey(Surgery, on_delete=models.CASCADE)
    surgeon = models.ForeignKey(Surgeon, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=0)

    class Meta:
        ordering = ['sequence']


class SurgeryDay(models.Model):
    date = models.DateField(verbose_name='Дата операции', unique=True)
    editable = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'День операции'
        verbose_name_plural = 'День операции'
    
    def __str__(self):
        return self.date.strftime('%d/%m/%Y')
