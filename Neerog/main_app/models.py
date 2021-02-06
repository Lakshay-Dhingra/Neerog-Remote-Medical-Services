from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Username and password will be in default User Model Provided by django
# Create your models here.

#Basic Details that we will take at registeration
class UserDetails(models.Model):
    userid = models.AutoField(primary_key=True)
    USER_TYPE_DEFAULT='Patient'
    USER_TYPE_CHOICES = [
        (USER_TYPE_DEFAULT, 'Patient'),
        ('Hospital', 'Hospital'),
        ('Doctor', 'Doctor'),
        ('Testing Lab', 'Testing Lab'),
    ]
    user_type=models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default=USER_TYPE_DEFAULT)   
    name = models.CharField(max_length=200)
    email=models.EmailField(max_length=254, unique=True, blank=False, null=False)
    created_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.userid)

    class Meta:
        verbose_name_plural='User Details'

    
#Patient will be deleted if its Userid is deleted in UserDetails
class Patient(models.Model):
    patientid = models.OneToOneField(UserDetails, on_delete=models.CASCADE, primary_key=True)
    phone=models.PositiveBigIntegerField(validators=[MaxValueValidator(9999999999),MinValueValidator(1000000000)], null=True) 
    about=models.TextField(max_length=500)
    country=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    address=models.CharField(max_length=200)
    DEFAULT_GENDER='U'
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Trans', 'Trans'),
        (DEFAULT_GENDER, 'Unknown'),
    ]
    gender=models.CharField(max_length=10, choices=GENDER_CHOICES, default=DEFAULT_GENDER)
    age=models.PositiveSmallIntegerField(validators=[MaxValueValidator(150),MinValueValidator(0)], null=True)

    DEFAULT_BLOOD='U'
    BLOOD_CHOICES = [
        ('A+ve', 'A+ve'),
        ('A-ve', 'A-ve'),
        ('B+ve', 'B+ve'),
        ('B-ve', 'B-ve'),
        ('AB+ve', 'AB+ve'),
        ('AB-ve', 'AB-ve'),
        ('O+ve', 'O+ve'),
        ('O-ve', 'O-ve'),
        ('HH+ve', 'HH+ve'),
        ('HH-ve', 'HH-ve'),
        (DEFAULT_BLOOD, 'Unknown'),
    ]
    blood_group=models.CharField(max_length=5, choices=BLOOD_CHOICES, default=DEFAULT_BLOOD)
    disability=models.CharField(max_length=50, default='None')
    profile_pic=models.ImageField(upload_to="patient_profile_photo/", null=True)

    def __str__(self):
        return str(self.patientid)

#Hospital will be deleted if its Userid is deleted in UserDetails
class Hospital(models.Model):
    # hospitalid = models.ForeignKey(UserDetails, on_delete=models.CASCADE, primary_key=True)
    hospitalid = models.OneToOneField(UserDetails, on_delete=models.CASCADE, primary_key=True)
    phone=models.PositiveBigIntegerField(validators=[MaxValueValidator(9999999999),MinValueValidator(1000000000)], null=True) 
    speciality = models.CharField(max_length=100)
    about=models.TextField(max_length=2000)
    country=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    address=models.CharField(max_length=200)
    year_established=models.PositiveIntegerField(validators=[MinValueValidator(1700)], null=True)
    hospital_logo=models.ImageField(upload_to="hospital_logo/", null=True)
    pic1=models.ImageField(upload_to="hospital_photo/", null=True)
    pic2=models.ImageField(upload_to="hospital_photo/", null=True)
    pic3=models.ImageField(upload_to="hospital_photo/", null=True)
    certificate=models.FileField(upload_to="hospital_certificate/", null=True)
    verified = models.CharField(max_length=10, default="No")

    def __str__(self):
        return str(self.hospitalid)

#Doctor will be deleted if its Userid is deleted in UserDetails
class Doctor(models.Model):
    # doctorid = models.ForeignKey(UserDetails, on_delete=models.CASCADE, primary_key=True)
    doctorid = models.OneToOneField(UserDetails, on_delete=models.CASCADE, primary_key=True, related_name="Doctor_set")
    phone=models.PositiveBigIntegerField(validators=[MaxValueValidator(9999999999),MinValueValidator(1000000000)], null=True) 
    specialization = models.CharField(max_length=100)
    about=models.TextField(max_length=500)
    country=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    address=models.CharField(max_length=200)
    DEFAULT_GENDER='U'
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Trans', 'Trans'),
        (DEFAULT_GENDER, 'Unknown'),
    ]
    gender=models.CharField(max_length=10, choices=GENDER_CHOICES, default=DEFAULT_GENDER)
    experience=models.PositiveSmallIntegerField(validators=[MaxValueValidator(100),MinValueValidator(0)], null=True)
    profile_pic=models.ImageField(upload_to="doctor_profile_photo/", null=True)
    certificate=models.FileField(upload_to="doctor_certificate/", null=True)

    #hospitalid will become null when a hospital is deleted
    hospitalid = models.ForeignKey(Hospital, models.SET_NULL, blank=True, null=True)
    clinic_name = models.CharField(max_length=100)
    clinic_photo = models.ImageField(upload_to="clinic_photo/", null=True)
    is_independent = models.BooleanField()
    verified = models.CharField(max_length=10, default="No")

    def __str__(self):
        return str(self.doctorid)

#TestingLab will be deleted if its Userid is deleted in UserDetails
class TestingLab(models.Model):
    # tlabid = models.ForeignKey(UserDetails, on_delete=models.CASCADE, primary_key=True)
    tlabid = models.OneToOneField(UserDetails, on_delete=models.CASCADE, primary_key=True)
    phone=models.PositiveBigIntegerField(validators=[MaxValueValidator(9999999999),MinValueValidator(1000000000)], null=True)
    about=models.TextField(max_length=2000)
    country=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    address=models.CharField(max_length=200)
    year_established=models.PositiveIntegerField(validators=[MinValueValidator(1700)], null=True)
    tlab_logo=models.ImageField(upload_to="testing_lab_logo/", null=True)
    pic1=models.ImageField(upload_to="testing_lab_photo/", null=True)
    certificate=models.FileField(upload_to="testing_lab_certificate/", null=True)
    verified = models.CharField(max_length=10, default="No")

    def __str__(self):
        return str(self.tlabid)

#The price will be deleted for a testing lab if it is deleted from TestingLab Model
class TestPricing(models.Model):
    tlabid = models.ForeignKey(TestingLab, on_delete=models.CASCADE)
    testname = models.CharField(max_length=100)
    price = models.PositiveIntegerField(null=True)

    def __str__(self):
        return str(self.tlabid)+" "+self.testname

    class Meta:
        unique_together = ('tlabid', 'testname',)

# Even if user or doctor gets deleted, this record shouldn't be deleted...
# class Appointments(models.Model):
#     appointmentid = models.AutoField(primary_key=True)
#     doctoremail = models.EmailField(max_length=254, unique=True, blank=False, null=False)
#     patientemail = models.EmailField(max_length=254, unique=True, blank=False, null=False)
#     hospitalemail = models.EmailField(max_length=254, unique=True)
#     amount_paid = models.PositiveIntegerField(unique=True)
#     appointment_date
#     appointment_time
#     etc... complete according to requirements
