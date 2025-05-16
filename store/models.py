from ckeditor.fields import RichTextField
from django.db import models
from autoslug import AutoSlugField
from django.utils.text import slugify
import os
from filer.fields.image import FilerImageField
from django_ckeditor_5.fields import CKEditor5Field


# функція для генерації імені для зображень товару
def generate_filename(instance, filename):
	base_filename, file_extension = os.path.splitext(filename)
	new_filename = f"{slugify(base_filename)}{file_extension}"
	return os.path.join('images/', new_filename)


class Category(models.Model):
	title = models.CharField(max_length=55)
	slug = models.SlugField(max_length=50)

	class Meta:
		verbose_name_plural = 'Категорії'

	def __str__(self):
		return self.title

class ChargerItemModel(models.Model):
	title = models.CharField(max_length=50)
	category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
	brand = models.CharField('Бренд', max_length=50, null=True, blank=True)
	description = models.TextField('Короткий опис', max_length=200, null=True)
	plugs = models.CharField('Доступні роз\'єми', max_length=50, null=True, blank=True)
	image = FilerImageField(on_delete=models.CASCADE)
	gif = FilerImageField(related_name='model_gif', on_delete=models.CASCADE, null=True, blank=True)
	slug = models.SlugField(max_length=50)

	class Meta:
		verbose_name_plural = 'Модель товару'

	def __str__(self):
		return self.title

class Currency(models.Model):
	title = models.CharField('Назва', max_length=50)
	current = models.DecimalField('Поточний курс до Евро', max_digits=5, decimal_places=2)
	token = models.CharField('Символ', max_length=10, blank=True)
	slug = AutoSlugField(populate_from='title', max_length=40, unique=True, default=None)


class ChargersItems(models.Model):
	TYPE_CHOICES = [
		('Type 1', 'type_1'), ('Type 2', 'type_2'), ('Type Tesla', 'type_tesla'), ('Type GBT', 'type_gbt')
	]
	PHASES_CHOICES = [
		('Одна фаза', '1_phase'), ('Три фази', '3_phase')
	]
	IN_STOCK_CHOICES = [
		('True', 'Активно'),
		('False', 'Неактивно'),
		('pending', 'Під замовлення'),
	]

	# ACCESSORIES_TYPE_CHOICES = [
	# 	('Тримач конектора', 'Trimach_conectora'),
	# 	('Кріплення\Тримач', 'Kriplennya_trimach'),
	# ]

	ACCESSORIES_TYPE_CHOICES = [
		('Trimach_conectora', 'Тримач конектора'),
		('Kriplennya_trimach', 'Кріплення\Тримач'),
		('electric_adapt', 'Електричні перехідники'),
		('auto_adapt', 'Електромобільні перехідники'),
		('plugs', 'Розетки'),
		('clothes', 'Одяг'),
		('other', 'Інше обладнання'),
	]

	category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
	title = models.CharField('Назва', max_length=70)
	product_article = models.CharField('Артикул', max_length=20, null=True, blank=True)
	slug = AutoSlugField(populate_from='title', max_length=100, unique=True, default=None)
	price = models.IntegerField('Ціна')
	sale_price = models.IntegerField('Ціна зі знижкою', null=True, blank=True)
	small_description = models.TextField('Короткий опис', max_length=600)
	description = CKEditor5Field('Опис', config_name='default')
	power = models.DecimalField('Потужність, кВт', blank=True, null=True, max_digits=8, decimal_places=1)
	power_amps = models.IntegerField('Потужність, А', blank=True, null=True)
	phases = models.TextField('Кількість фаз', blank=True, null=True, choices=PHASES_CHOICES)
	type = models.CharField('Тип роз\'єму', max_length=10, null=True, blank=True, choices=TYPE_CHOICES)
	cable_length = models.IntegerField('Довжина кабелю', blank=True, null=True)
	protection = models.CharField('Захист корпусу', max_length=10, null=True, blank=True)
	set = models.CharField('Комплектація', max_length=15, null=True, blank=True)
	guarantee = models.CharField('Гарантія', max_length=10, blank=True, null=True)
	brand = models.CharField('Бренд', max_length=20, blank=True, null=True)
	country = models.CharField('Країна-виробник', max_length=20, blank=True, null=True)
	form = models.CharField('Формфактор', max_length=15, null=True, blank=True)
	features = models.TextField('Додаткові функції', max_length=200, null=True, blank=True)
	time = models.DateTimeField('Дата створення', auto_now_add=True, null=True)
	size = models.CharField("Розмір", max_length=15, blank=True, null=True)
	material = models.CharField("Матеріал", max_length=50, blank=True, null=True)
	accessories_type = models.CharField("Тип аксесуару", max_length=50, blank=True, null=True, choices=ACCESSORIES_TYPE_CHOICES)
	model = models.ManyToManyField(ChargerItemModel, blank=True)
	in_stock = models.CharField('Наявність', max_length=20, null=True, blank=True, choices=IN_STOCK_CHOICES)

	class Meta:
		verbose_name_plural = 'Зарядні пристрої'

	def __str__(self):
		return self.title


	@classmethod
	def get_accessories_type_dict(cls):
		return dict(cls.ACCESSORIES_TYPE_CHOICES)


class Gallery(models.Model):
	title = models.CharField("Ім\'я файлу", max_length=200, blank=True)
	image = FilerImageField(on_delete=models.CASCADE)
	chargersitems = models.ForeignKey(ChargersItems, on_delete=models.CASCADE, null=True)

	class Meta:
		verbose_name = 'Галерея фото'
		verbose_name_plural = 'Галерея фото'

class FavoriteProducts(models.Model):
	products = models.ForeignKey(ChargerItemModel, on_delete=models.CASCADE, null=True, blank=True)
	class Meta:
		verbose_name = 'Обрані товари'
		verbose_name_plural = 'Обрані товари'

class FavoriteAccessories(models.Model):
	products = models.ForeignKey(ChargersItems, on_delete=models.CASCADE, null=True, blank=True)
	class Meta:
		verbose_name = 'Обрані аксесуари'
		verbose_name_plural = 'Обрані аксесуари'