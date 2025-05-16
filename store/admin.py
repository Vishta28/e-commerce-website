from django.contrib import admin
from django.shortcuts import render
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.db import models

from .models import ChargerItemModel, Category, ChargersItems, Gallery, Currency, FavoriteProducts, FavoriteAccessories
from django.utils.html import format_html


admin.site.register(Category)
admin.site.register(ChargerItemModel)


class GalleryInline(admin.StackedInline):
    model = Gallery
    extra = 1  # Додаткові поля для видалення
    can_delete = True


class ChargersItemsAdmin(admin.ModelAdmin):
    inlines = [
        GalleryInline,
    ]
    filter_horizontal = ('model',)
    fieldsets = [
        (
            None,
            {
                "fields": ["title", "product_article", "small_description", "description", "price", "sale_price", "brand", "country", "features",
                           "guarantee", "in_stock", "category"],
            },
        ),
        (
            "Поля для зарядного обладнання",
            {
                "fields": ["power", "power_amps", "phases", "type", "cable_length", "protection", "form",
                           "model"],
                "classes": ["collapse"],
            },
        ),
        (
            "Поля для аксесуарів",
            {
                "fields": ["size", "material", "accessories_type"],
                "classes": ["collapse"],  # це робить вкладку Accessories Fields згортнутою
            },
        ),
    ]




admin.site.register(FavoriteProducts)
admin.site.register(FavoriteAccessories)
admin.site.register(ChargersItems, ChargersItemsAdmin)
admin.site.register(Currency)


# class AttachmentChargersItemsAdmin(admin.ModelAdmin):
#     def image_tag(self, obj):
#         return format_html('<img src="{}" style="max-width:150px; max-height:150px"/>'.format(obj.gallery.images.url))
#
#     image_tag.short_description = 'Image'
#     list_display = ['chargeritem', 'gallery', 'image_tag']
#
# admin.site.register(AttachmentChargersItems ,AttachmentChargersItemsAdmin)

# class AdminImageWidget(AdminFileWidget):
#     def render(self, name, value, attrs=None, renderer=None):
#         output = []
#         if value and getattr(value, "url", None):
#             image_url = value.url
#             file_name = str(value)
#             output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" width="150" height="150"  style="object-fit: cover;"/></a> %s ' % \
#                 (image_url, image_url, file_name, ('')))
#         output.append(super().render(name, value, attrs, renderer))  # Викликаємо метод render батьківського класу
#         return mark_safe(u''.join(output))
