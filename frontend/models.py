from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from django.utils.timezone import now

class Submission(models.Model):
  patient_id = models.CharField(max_length=100, db_index=True)
  author = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
  submission_type = models.CharField(max_length=10)
  submission_status = models.CharField(max_length=10)
  sex = models.CharField(max_length=10)
  age = models.IntegerField(default=0)
  fever_temp = models.DecimalField(default=0, max_digits=4, decimal_places=2)
  fever_duration = models.IntegerField(default=0)
  interpretation = models.CharField(max_length=100)
  comorbidities = models.CharField(max_length=100)

  file_location = models.CharField(max_length=1000)
  file_location_result = models.CharField(max_length=1000, null=True, default="")



  ts_submission = models.DateTimeField(default=now)
  ts_update = models.DateTimeField(default=now)

  cough = models.BooleanField(default=False)
  flu = models.BooleanField(default=False)
  sore_throat = models.BooleanField(default=False)
  shiver = models.BooleanField(default=False)
  headache = models.BooleanField(default=False)
  faint = models.BooleanField(default=False)
  hard_to_breathe = models.BooleanField(default=False)
  nausea = models.BooleanField(default=False)
  diarrhea = models.BooleanField(default=False)
  muscleache = models.BooleanField(default=False)
  abdominal_pain = models.BooleanField(default=False)
  other_conditions = models.CharField(max_length=100)

  prediction = models.CharField(max_length=100,default="-")
  prob_normal = models.DecimalField(default=0, max_digits=8, decimal_places=5)
  prob_pneu = models.DecimalField(default=0, max_digits=8, decimal_places=5)
  prob_covid = models.DecimalField(default=0, max_digits=8, decimal_places=5)

  def prob_normal_percentage(self):
    return round(self.prob_normal * 100, 2)
  def prob_pneu_percentage(self):
    return round(self.prob_pneu * 100, 2)
  def prob_covid_percentage(self):
    return round(self.prob_covid * 100, 2)

  prediction = models.CharField(max_length=100,default="-")


  class Meta:
      verbose_name = 'Submission'
      verbose_name_plural = 'Submissions'
      unique_together = ("patient_id", "author")

class Contact(models.Model):
  name = models.CharField(max_length=100, db_index=True)
  email = models.CharField(max_length=100)
  subject = models.CharField(max_length=100)
  message = models.CharField(max_length=1000)

  class Meta:
      verbose_name = 'Contact'
      verbose_name_plural = 'Contacts'
