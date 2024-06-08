from django.contrib import admin
from .models import *
from .forms import PlanForm
# Register your models here.
admin.site.register(Atrakcja)
admin.site.register(Znizka)
class PlanAdmin(admin.ModelAdmin):
    form = PlanForm

admin.site.register(Plan, PlanAdmin)
admin.site.register(Kategorie)
admin.site.register(PlanyUzytkownika)