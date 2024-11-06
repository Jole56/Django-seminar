from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Korisnik(AbstractUser):
    roles = (('admin','administrator'),('prof','profesor'),('stud','student'))
    role = models.CharField(max_length=50,choices=roles)
    statuses = (('none','none'),('izv','izvanredni'),('red','redovni'))
    status = models.CharField(max_length=50,choices=statuses)


class Predmeti(models.Model):
    name = models.CharField(max_length=255)
    kod = models.CharField(max_length=16)
    program = models.CharField(max_length=255)
    sem_red = models.IntegerField()
    sem_izv = models.IntegerField()
    ects = models.IntegerField()

    izbor = (('da','da'),('ne','ne'))
    izborni = models.CharField(max_length=10,choices=izbor)

    nositelj = models.ForeignKey(Korisnik,on_delete=models.SET_NULL,null=True,limit_choices_to={'role':'prof'})
    
    def __str__(self):
        return self.name


class Upisi(models.Model):
    student = models.ForeignKey(Korisnik,on_delete=models.CASCADE)
    predmet = models.ForeignKey(Predmeti,on_delete=models.CASCADE)
    statusi = (('failed','failed'),('passed','passed'),('enr','enrolled'),('nenr','notEnrolled'))
    status = models.CharField(max_length=50,choices=statusi)
    class Meta:
        unique_together = ('student','predmet')