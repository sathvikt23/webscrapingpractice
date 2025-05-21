from django.shortcuts import render
from django.http import JsonResponse 
from . serializers import *
from .models import *
import json
def hello_api(request):
    if request.method=="GET":
        rawdata=employee.objects.select_related("dept_id").get()
        data=Employee(rawdata)
        return JsonResponse({f"message":f"{data.data}"})
# Create your views here.

def create_student(request):
    if request.method=="POST":
       data=json.loads(request.body)
       print(data)
       
       emp =employee.objects.create(id=data["emp_id"], dept_id_id=data["dept_id"],name=data["emp_name"], age=data["age"])
       #dep =department.objects.create(dept_id=data["dept_id"],name=data["department"])
       
       #response={"1":emp,"2":dep}

       return JsonResponse({"message":"created"})
def create_department(request):
    if request.method=="POST":
       data=json.loads(request.body)
       print(data)
       dep =department.objects.create(dept_id=data["dept_id"],name=data["department"])
     
       #dep =department.objects.create(dept_id=data["dept_id"],name=data["department"])
       
       #response={"1":emp,"2":dep}

       return JsonResponse({"message":"created"})
