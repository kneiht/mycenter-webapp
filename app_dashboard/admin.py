from .models import *




from django.contrib import admin
from django.apps import apps

class DefaultModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        # Get all field names from the model
        return [field.name for field in self.model._meta.fields]

    def get_search_fields(self, request):
        # Get all character/text field names for searching
        return [field.name for field in self.model._meta.fields 
                if field.get_internal_type() in ['CharField', 'TextField']]

# Get all models from your app
app_models = apps.get_app_config('app_dashboard').get_models()

# Register any model that hasn't been registered yet with the default admin class
for model in app_models:
    try:
        admin.site.register(model, DefaultModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass

# Your existing custom admin classes below