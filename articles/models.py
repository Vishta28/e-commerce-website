from autoslug import AutoSlugField
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from filer.fields.image import FilerImageField


# Create your models here.
class ArticleModel(models.Model):
	ARTICLE_TYPE = [
		('user_article', 'Для користувачів'), ('tech_article', 'Технічна стаття')
	]

	title = models.CharField('Назва', max_length=200)
	image = FilerImageField(on_delete=models.CASCADE, null=True, blank=True)
	slug = AutoSlugField(populate_from='title', max_length=150, unique=True, default=None)
	main_text = CKEditor5Field('Опис', config_name='default')
	tags = models.CharField('Теги', max_length=200, blank=True, null=True)
	time = models.DateTimeField('Дата створення', auto_now_add=True, null=True)
	article_type = models.CharField('Тип статті', max_length=30, null=True, blank=True, choices=ARTICLE_TYPE)

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = 'Стаття'
		verbose_name_plural = 'Статті'
