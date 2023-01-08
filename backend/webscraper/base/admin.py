from django.contrib import admin

from . import models


admin.site.register(models.Spider)
admin.site.register(models.Template)
admin.site.register(models.Inspector)
admin.site.register(models.Runner)
