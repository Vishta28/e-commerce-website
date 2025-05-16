def get_first_image(context):
	try:
		chargersitems = context['items']
		print(chargersitems, 'ITEMS')
	except:
		chargersitems = context
		print(chargersitems, 'ITEMS2')

	chargersitems_images = {}

	for item in chargersitems:
		images = item.gallery_set.filter(chargersitems_id=item.id)
		# Отримати всі екземпляри AttachmentAccessories, які відповідають поточному аксесуару
		# Припускається, що у моделі AttachmentAccessories є ForeignKey до моделі Gallery
		if images:
			for image in images[:1]:
				chargersitems_images[item.slug] = [image.image.url]
				print(chargersitems_images[item.slug], 'SLUG')
		else:
			chargersitems_images[item.slug] = None

	return chargersitems_images

def get_first_image_favorite_products(context):
	chargersitems = context

	chargersitems_images = {}

	for item in chargersitems:
		images = item.products.gallery_set.filter(chargersitems_id=item.products.id)
		# Отримати всі екземпляри AttachmentAccessories, які відповідають поточному аксесуару
		# Припускається, що у моделі AttachmentAccessories є ForeignKey до моделі Gallery
		if images:
			for image in images[:1]:
				chargersitems_images[item.products.slug] = [image.image.url]
		else:
			chargersitems_images[item.products.slug] = None

	return chargersitems_images


def get_all_images(context):
	try:
		chargersitems = context['item']
	except:
		chargersitems = context

	chargersitems_images = {}

	if chargersitems:
		images = chargersitems.gallery_set.filter(chargersitems_id=chargersitems.id)
		# Отримати всі екземпляри AttachmentAccessories, які відповідають поточному аксесуару
		# Припускається, що у моделі AttachmentAccessories є ForeignKey до моделі Gallery
		if images:
			chargersitems_images[chargersitems.slug] = [image.image.url for image in images]
			print(chargersitems_images, 'Images')
		else:
			chargersitems_images[chargersitems.slug] = None
	return chargersitems_images

def get_all_imagesA(context):
	try:
		accessories = context['item']
	except:
		accessories = context

	accessories_images = {}

	if accessories:
		# Отримати всі екземпляри AttachmentAccessories, які відповідають поточному аксесуару
		attachment_accessories = accessories.attachmentaccessories_set.all()
		# Припускається, що у моделі AttachmentAccessories є ForeignKey до моделі Gallery
		if attachment_accessories:
			accessories_images[accessories.slug] = [attachment.gallery.images.url for attachment in
														attachment_accessories]
		else:
			accessories_images[accessories.slug] = None

	return accessories_images

def get_first_imageA(context):
	try:
		accessories = context['items']
	except:
		accessories = context
	accessories_images = {}

	for item in accessories:
		# Отримати всі екземпляри AttachmentAccessories, які відповідають поточному аксесуару
		attachment_accessories = item.attachmentaccessories_set.all()
		# Припускається, що у моделі AttachmentAccessories є ForeignKey до моделі Gallery
		if attachment_accessories:
			accessories_images[item.slug] = [attachment_accessories.first().gallery.images.url]
		else:
			accessories_images[item.slug] = None

	return accessories_images
