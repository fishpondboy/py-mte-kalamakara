from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Submission, Contact
# Register your models here.

class SubmissionResource(resources.ModelResource):
  class Meta:
    model = Submission

class SubmissionAdmin(ImportExportModelAdmin):
  resource_class = SubmissionResource
  # list_display = ['name', 'description', 'center_longitude', 'center_latitude', 'credit_required', 'token']


class ContactResource(resources.ModelResource):
  class Meta:
    model = Contact

class ContactAdmin(ImportExportModelAdmin):
  resource_class = ContactResource

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Contact, ContactAdmin)
