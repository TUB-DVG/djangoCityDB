from django.contrib import admin
import citydb.models as citydb
from django.apps import apps
# import .models

# Get a list of all models in the current module
attributesOfCityDB = dir(citydb)
modelNames = [item for item in attributesOfCityDB if not item.startswith('__')]
# models = [m for m in globals().values() if isinstance(m, type) and issubclass(m, models.Model) and m != models.Model]

# Register all the models with the admin site
for model in modelNames:
    modelClass = apps.get_model('citydb', model)
    admin.site.register(modelClass)