from django.contrib import admin
from sentiment.models import Org,Product,Review,Video,Audio

# Register your models here.
class OrgAdmin(admin.ModelAdmin):
    list_display=['name']

class ProductAdmin(admin.ModelAdmin):
    list_display=['name']

class ReviewAdmin(admin.ModelAdmin):
    list_display=['text']

class VideoAdmin(admin.ModelAdmin):
    list_display=['product']

class AudioAdmin(admin.ModelAdmin):
    list_display=['product']

admin.site.register(Org,OrgAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Review,ReviewAdmin)
admin.site.register(Video,VideoAdmin)
admin.site.register(Audio,AudioAdmin)
