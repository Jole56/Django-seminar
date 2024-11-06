from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .forms import FormKorisnik,CustomAuthenticationForm,FormPredmet,FormLogout,FormUpisniList,FormEditKorisnik,FormAssignNositelj,EditStudentStatusForm
from .models import Korisnik,Upisi,Predmeti
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from django.db.models import Q,Sum
# Create your views here.
def home(request):
    nesto="Welcome"
    return render(request,'home.html',{'nesto':nesto})


def add_korisnik(request):
    if request.method == 'GET':
        form = FormKorisnik()
        return render(request,'add_korisnik.html',{'form':form})
    elif request.method == 'POST':
        form = FormKorisnik(request.POST)
        if form.is_valid():
            print(form.cleaned_data.get('password1'))
            print(form.cleaned_data)
            form.save()
            return redirect('all_users')
        
def login_user(request):
    if request.method == 'POST':
        form =  CustomAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request,username = username,password = password)
            if user is not None:
                login(request,user)
                if user.role == 'stud':
                    return redirect('profileStudent')
                elif user.role == 'admin':
                    return redirect('adminPanel')
                elif user.role == 'prof':
                    return redirect('profileProfesor')
            else:
                form.add_error(None,'Invalid username or password!')
    else:
        form = CustomAuthenticationForm()
    return render(request,'login.html',{'form':form})

@login_required
def logout_fun(request):
    if request.method == 'POST':
        form = FormLogout(request.POST)
        if form.is_valid():
            logout(request)
            return redirect('login')
    else:
        form = FormLogout()
    return render(request,'logout.html',{'form':form})

@login_required
def profileStudent(request):
    student = Korisnik.objects.get(id=request.user.id)
    predmeti = Predmeti.objects.all()
    # upisi = Upisi.objects.filter(student=student)
    polozeni_predmeti_prva_god = []
    polozeni_predmeti_druga_god = []
    # predmeti = [upis.predmet for upis in upisi]
    upisani_predmeti = Upisi.objects.filter(student=student).values_list('predmet_id', flat=True)
    polozeni_predmeti = Upisi.objects.filter(student=student, status='passed').values_list('predmet_id', flat=True)
    print("Polozeni:"+str(polozeni_predmeti))
    prvi_drugi_semestar = Predmeti.objects.filter(Q(sem_red=1) | Q(sem_red=2))
    treci_cetvrti_semestar = Predmeti.objects.filter(Q(sem_red=3) | Q(sem_red=4))
    prvi_drugi_semestar_ids = prvi_drugi_semestar.values_list('id', flat=True)
    treci_cetvrti_semestar_ids = treci_cetvrti_semestar.values_list('id', flat=True)
    #print("Predmeti 1. i 2. semestar"+str(prvi_drugi_semestar))
    polozeni_predmeti_prva_god = [predmet_id for predmet_id in prvi_drugi_semestar_ids if predmet_id in polozeni_predmeti]
    polozeni_predmeti_druga_god = [predmet_id for predmet_id in treci_cetvrti_semestar_ids if predmet_id in polozeni_predmeti]
    svi_prvi_drugi_polazeni = set(prvi_drugi_semestar_ids) == set(polozeni_predmeti_prva_god)
    svi_treci_cetvrti_polazeni = set(treci_cetvrti_semestar_ids) == set(polozeni_predmeti_druga_god)
    print("Polozeni sa prve godine"+str(polozeni_predmeti_prva_god))
    print("Polozeni sa druge godine"+str(polozeni_predmeti_druga_god))
    svi_predmeti_polozeni = svi_prvi_drugi_polazeni and svi_treci_cetvrti_polazeni
    # Podesi zastavicu upisan za svaki predmet
    for predmet in predmeti:
        if predmet.id in upisani_predmeti:
            predmet.upisan = True
        else:
            predmet.upisan = False
    prikazani_predmeti=[]
    for predmet in predmeti:
        if svi_predmeti_polozeni:
            prikazani_predmeti.append(predmet)
        else:
            if predmet.sem_red > 2 and not svi_prvi_drugi_polazeni:
                continue
        
            # if predmet.sem_red > 4 and not svi_treci_cetvrti_polazeni:
            #     continue
            prikazani_predmeti.append(predmet)
    print("Prikazani:"+str(prikazani_predmeti))
    return render(request, 'profileStudent.html', {'predmeti': prikazani_predmeti})

@login_required
def enroll_predmet(request, predmet_id):
    student = Korisnik.objects.get(id=request.user.id)
    predmet = Predmeti.objects.get(id=predmet_id)
    upisani_predmeti = Upisi.objects.filter(student=student).values_list('predmet_id', flat=True)
    
    if Upisi.objects.filter(student=student, predmet=predmet).exists():
        return redirect('profileStudent')
    
    Upisi.objects.create(student=student, predmet=predmet, status='enrolled')
    return redirect('profileStudent')

@login_required
def withdraw_predmet(request, predmet_id):
    student = Korisnik.objects.get(id=request.user.id)
    predmet = Predmeti.objects.get(id=predmet_id)
    

    upis = Upisi.objects.filter(student=student, predmet=predmet).first()
    if not upis:
        return redirect('profileStudent')

    upis.delete()
    return redirect('profileStudent')

@login_required
def profesorPredmets(request):
    predmet_sa_studentima = []
    profesor = request.user
    predmeti = Predmeti.objects.filter(nositelj=profesor)
    print(predmeti)
    for subject in predmeti:
        upisi = Upisi.objects.filter(predmet=subject).exclude(status='nenr')
        print(upisi)
        studenti_sa_statusima = [{'student':upis.student,'status':upis.status} for upis in upisi]
        predmet_sa_studentima.append({'subject':subject,'studenti':studenti_sa_statusima})
    sort_key = request.GET.get('sort', '')
    for predmet in predmet_sa_studentima:
        studenti = predmet['studenti']
        if sort_key == 'lost':
            studenti.sort(key=lambda x: 0 if x['status'] == 'failed' else (1 if x['status'] == 'enr' else 2))
        elif sort_key == 'pending':
            studenti.sort(key=lambda x: 0 if x['status'] == 'enr' else (1 if x['status'] == 'passed' else 2))
        elif sort_key == 'passed':
            studenti.sort(key=lambda x: 0 if x['status'] == 'passed' else (1 if x['status'] == 'enr' else 2))

    return render(request,'profesorPredmets.html',{'predmet_sa_studentima':predmet_sa_studentima})

def profesorProfile(request):
    return render(request,'profileProfesor.html',{})

@login_required
def all_users(request):
    users = Korisnik.objects.all()
    return render(request,'all_users.html',{'users':users})

@admin_required
def add_predmet(request):
    if request.method == 'POST':
        form = FormPredmet(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = FormPredmet()
    return render(request,'add_predmet.html',{'form':form})

def display_all_upisi(request):
    upisi = Upisi.objects.all()
    return render(request,'all_upisi.html',{'upisi':upisi})


def display_all_students(request):
    students = Korisnik.objects.filter(role='stud')
    #print("Studenti: "+str(students))
    return render(request,'all_students.html',{'students':students})

def student_upisni_list(request,studentID):
    upisni = Upisi.objects.filter(student=Korisnik.objects.get(pk=studentID)).all()
    print(upisni)
    return render(request,'upisni_list.html',{'upisni':upisni})

def add_upisni_list(request):
    if request.method == 'POST':
        form = FormUpisniList(request.POST)
        if form.is_valid():
            form.save()
            return redirect("add_upisni_list")
    else:
        form = FormUpisniList()
    return render(request,'add_upisni_list.html',{'form':form})

@admin_required
def adminPanel(request):
    admin = request.user.username
    return render(request,'adminPanel.html',{'admin':admin})

def display_all_predmets(request):
    predmets = Predmeti.objects.all()
    return render(request,'all_predmets.html',{'predmets':predmets})

def display_all_profesors(request):
    profesors = Korisnik.objects.filter(role='prof')
    print("Profesori: "+str(profesors))
    return render(request,'all_profesors.html',{'profesors':profesors})


def edit_predmet(request,predmetID):
    predmet = Predmeti.objects.get(id=predmetID)
    print(predmet)
    if request.method == 'POST':
        form = FormPredmet(request.POST, instance=predmet)
        if form.is_valid():
            form.save()
            return redirect('all_predmets')
        
    else:
        form = FormPredmet(instance=predmet)
    return render(request,'edit_predmet.html',{'form':form})


def edit_student(request,studentID):
    student = Korisnik.objects.get(pk = studentID)
    print(student)
    if request.method == 'POST':
        form = FormEditKorisnik(request.POST,instance=student)
        if form.is_valid():
            form.save()
            return redirect('all_students')
    else:
        form = FormEditKorisnik(instance=student)
    return render(request,'edit_student.html',{'form':form})


def edit_profesor(request,profesorID):
    profesor = Korisnik.objects.get(pk = profesorID)
    print(profesor)
    if request.method == 'POST':
        form = FormEditKorisnik(request.POST,instance=profesor)
        if form.is_valid():
            form.save()
            return redirect('all_profesors')
    else:
        form = FormEditKorisnik(instance=profesor)
    return render(request,'edit_profesor.html',{'form':form})


def edit_upis(request,upisID):
    upis = Upisi.objects.get(pk = upisID)
    print(upis)
    if request.method == 'POST':
        form = FormUpisniList(request.POST,instance=upis)
        if form.is_valid():
            form.save()
            return redirect('all_upisi')
    else:
        form = FormUpisniList(instance=upis)
    return render(request,'edit_upis.html',{'form':form})



def assign_nositelj(request):
    if request.method == 'POST':
        form = FormAssignNositelj(request.POST)
        if form.is_valid():
            predmet = form.cleaned_data['predmeti']
            nositelj = form.cleaned_data['nositelj']
            try:
                predmet.nositelj = nositelj
                predmet.save(update_fields=['nositelj'])
                return redirect('assignNositelj')
            except Exception as e:
                form.add_error(None, f'Greška prilikom ažuriranja predmeta: {e}')
    else:
        form = FormAssignNositelj()
    return render(request, 'assign_nositelj.html', {'form': form})


def edit_student_status(request, studentID, subjectID):
    student = Korisnik.objects.get(id = studentID)
    predmet = Predmeti.objects.get(id = subjectID)
    print(student)
    print(predmet)
    upis = Upisi.objects.filter(student=student,predmet=predmet)
    if request.method == 'POST':
        form = EditStudentStatusForm(request.POST)
        if form.is_valid():
            novi_status = form.cleaned_data['status']
            upis.update(status=novi_status)
            return redirect('profileProfesor')
    else:
        form = EditStudentStatusForm()
    return render(request,'edit_student_status.html',{'form':form,'student':student,'subjectID':subjectID})


def studenti_sa_vise_od_10_ects(request):
    upisi = Upisi.objects.exclude(status='nenr')
    student_ects = upisi.values('student__username').annotate(total_ects=Sum('predmet__ects'))
    studenti = student_ects.filter(total_ects__gt=10)
    studenti_s_imenima=[]
    for student in studenti:
        studenti_s_imenima.append(student['student__username'])
    return render(request, 'studenti_sa_vise_od_10_ects.html', {'studenti': studenti_s_imenima})