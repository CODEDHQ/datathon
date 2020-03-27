from django.contrib import admin
from django.urls import resolve
from .models import *


class QuestionInline(admin.TabularInline):
	model = Question
	extra = 1
	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if db_field.name == "prerequisites":
			kwargs["queryset"] = Question.objects.filter(dataset=self.parent_model.objects.get(pk=resolve(request.path_info).kwargs['object_id']))
		return super(QuestionInline, self).formfield_for_manytomany(db_field, request, **kwargs)


class DatasetAdmin(admin.ModelAdmin):
	inlines = [QuestionInline]

	def get_formsets(self, request, obj=None, *args, **kwargs):
		for inline in self.inline_instances:
			inline._parent_instance = obj
			yield inline.get_formset(request, obj)


admin.site.register(Team)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Level)
