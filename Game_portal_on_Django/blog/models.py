from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models.functions import datetime
from django.urls import reverse
from slugify import slugify
from django.utils import timezone


class GamePost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Проект'),
        ('published', 'Изданный'),
    ]
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    excerpt = RichTextField(blank=True, help_text='Краткое содержание статьи', verbose_name='Кратко')
    content = RichTextUploadingField(blank=True, verbose_name='Статья')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name='Фото')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время редактирования')
    publish = models.DateTimeField(default=timezone.now, verbose_name='Время публикации')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория')
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Автор")
    tags = models.ManyToManyField('TagArticle', blank=True, related_name='tags')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Статьи о играх'
        verbose_name_plural = 'Статьи о играх'
        ordering = ['-time_create', 'title', '-publish']


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Категория')
    description = models.TextField(blank=True, verbose_name='Описание')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = 'Категории игр'
        verbose_name_plural = 'Категории игр'


class Comment(models.Model):
    article_id = models.ForeignKey(GamePost, on_delete=models.CASCADE, verbose_name='Статья')
    author_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    email = models.EmailField(verbose_name='e-mail')
    content = models.TextField(blank=True, verbose_name='Комментарий')
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", blank=True, verbose_name='Фото')
    photo1 = models.ImageField(upload_to="photos/%Y/%m/%d/", blank=True, verbose_name='Фото1')
    photo2 = models.ImageField(upload_to="photos/%Y/%m/%d/", blank=True, verbose_name='Фото2')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Время редактирования')
    active = models.BooleanField(default=True, verbose_name='Опубликовать?')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарий'
        ordering = ('created',)

    def __str__(self):
        return 'Комментарий от {} для {}'.format(self.author_id, self.article_id)


class TagArticle(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})


class NewsBlock(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, help_text='Максимум 255 символов.',
                             verbose_name='Название новости')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="Slug", validators=[
        MinLengthValidator(5, message="Минимум 5 символов"),
        MaxLengthValidator(100, message="Максимум 100 символов"),
    ])
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default=None,
                              blank=True, null=True, help_text='Картинка к новости', verbose_name="Фото")
    excerpt = RichTextField(blank=True,
                            help_text='Краткое содержание новости, заполнять не обязательно.',
                            verbose_name='Кратко')
    content = RichTextUploadingField(help_text='', verbose_name='Подробно')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    pub_date = models.DateTimeField(default=datetime.datetime.now, verbose_name='Дата публикации')
    status = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                 default=Status.DRAFT, verbose_name="Статус")
    tags = models.ManyToManyField('TagNews', blank=True, related_name='tags')

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Новости'
        verbose_name = 'Новость'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news', kwargs={'news_slug': self.slug})


class TagNews(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('tag_news', kwargs={'tag_news_slug': self.slug})
