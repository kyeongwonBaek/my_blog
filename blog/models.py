from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown


class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural ='categories'
    def get_absolute_url(self):
        return '/blog/category/{}/'.format(self.slug)
class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/blog/tag/{}/'.format(self.slug)

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = MarkdownxField()
    head_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)
    created = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=True)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, null=True, blank=True)

    def __str__(self):
        return '{}::{}'.format(self.title, self.author)
    
    def get_absolute_url(self):
        return '/blog/{}/'.format(self.pk)

    def get_markdown_content(self):
        return markdown(self.content)
