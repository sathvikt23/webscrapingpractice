from rest_framework import serializers
from . models import *
class Department(serializers.ModelSerializer):
    class Meta :
        model =department
        feilds='__all__'
class Employee(serializers.ModelSerializer):

    class Meta :
        model = employee
        fields='__all__'