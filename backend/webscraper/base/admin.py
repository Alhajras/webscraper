from django.contrib import admin

from . import models


admin.site.register(models.Crawler)
admin.site.register(models.Template)
admin.site.register(models.Inspector)
admin.site.register(models.InspectorValue)
admin.site.register(models.Runner)
admin.site.register(models.Indexer)
