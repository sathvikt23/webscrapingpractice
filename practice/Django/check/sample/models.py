from django.db import models

# Create your models here.


class department(models.Model):
    dept_id=models.IntegerField(primary_key=True)
    name=models.CharField(max_length=200)

class employee (models.Model):
    id=models.IntegerField(primary_key=True,unique=True)
    name=models.CharField(max_length=200)
    age=models.IntegerField()
    dept_id=models.ForeignKey(department,on_delete=models.CASCADE)

