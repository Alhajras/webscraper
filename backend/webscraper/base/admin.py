from django.contrib import admin

from . import models


admin.site.register(models.Crawler)
admin.site.register(models.Template)
admin.site.register(models.Inspector)
admin.site.register(models.InspectorValue)
admin.site.register(models.Runner)
admin.site.register(models.Indexer)
admin.site.register(models.ActionChain)
admin.site.register(models.Action)
admin.site.register(models.WaitAction)
admin.site.register(models.ClickAction)
admin.site.register(models.ScrollAction)
admin.site.register(models.Document)
