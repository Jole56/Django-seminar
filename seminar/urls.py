"""
URL configuration for seminar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app_1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adminPanel/',views.adminPanel,name="adminPanel"),
    path('adminPanel/register',views.add_korisnik,name='register'),
    path('login_user', views.login_user, name='login'),
    path('all_users',views.all_users,name='all_users'),
    path('adminPanel/add_predmet',views.add_predmet,name='add_predmet'),
    path('adminPanel/all_upisi',views.display_all_upisi,name='all_upisi'),
    path('logout',views.logout_fun,name='logout'),
    path('profileStudent',views.profileStudent,name='profileStudent'),
    path('profileStudent/enroll/<int:predmet_id>/', views.enroll_predmet, name='enroll_predmet'),
    path('profileStudent/withdraw/<int:predmet_id>/', views.withdraw_predmet, name='withdraw_predmet'),
    path('profileProfesor',views.profesorProfile,name='profileProfesor'),
    path('profesorPredmets',views.profesorPredmets,name='profesorPredmets'),
    path('adminPanel/all_students',views.display_all_students,name="all_students"),
    path('adminPanel/all_predmets',views.display_all_predmets,name="all_predmets"),
    path('adminPanel/all_profesors',views.display_all_profesors,name="all_profesors"),
    path('student/<int:studentID>/upisni_list',views.student_upisni_list,name="student_upisni_list"),
    path('adminPanel/add_upisni_list',views.add_upisni_list,name="add_upisni_list"),
    path('adminPanel/editPredmet/<int:predmetID>',views.edit_predmet,name="editPredmet"),
    path('adminPanel/editStudent/<int:studentID>',views.edit_student,name="editStudent"),
    path('adminPanel/editProfesor/<int:profesorID>',views.edit_profesor,name="editProfesor"),
    path('adminPanel/editUpis/<int:upisID>',views.edit_upis,name="editUpis"),
    path('adminPanel/assignNositelj',views.assign_nositelj,name="assignNositelj"),
    path('editStatus/<int:studentID>/<int:subjectID>',views.edit_student_status,name="editStatus"),
    path('studenti10ects',views.studenti_sa_vise_od_10_ects,name="studenti10ects"),
    path('home',views.home,name='home')


]
