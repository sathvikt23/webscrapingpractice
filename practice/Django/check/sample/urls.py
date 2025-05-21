from django.contrib import admin
from django.urls import path
from . import views 
urlpatterns = [
    path('admin/', admin.site.urls),
    path("",views.hello_api),
    path("created/",views.create_department),
    path("createe/",views.create_student)
]
