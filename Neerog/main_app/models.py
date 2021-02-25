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
    about=models.TextField(max_length=500, blank=True)
    country=models.CharField(max_length=50, blank=True)
    city=models.CharField(max_length=50, blank=True)
    address=models.CharField(max_length=200, blank=True)
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
    disability=models.CharField(max_length=50, default='NO')
    profile_pic=models.ImageField(upload_to="patient_profile_photo/", blank=True, null=True)

    nullable_strings=[about, country, city, address, blood_group]
    nullable_non_strings=[profile_pic]

    def __str__(self):
        return str(self.patientid)

    def save(self, *args, **kwargs):
        for i in self.nullable_non_strings:
            if not i:
                self.i = None
        for i in self.nullable_strings:
            if not i:
                self.i = ""
        super(Patient, self).save(*args, **kwargs)


#Hospital will be deleted if its Userid is deleted in UserDetails
class Hospital(models.Model):
    hospitalid = models.OneToOneField(UserDetails, on_delete=models.CASCADE, primary_key=True)
    phone=models.PositiveBigIntegerField(validators=[MaxValueValidator(9999999999),MinValueValidator(1000000000)], null=True) 
    about=models.TextField(max_length=2000)
    country=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    area=models.CharField(max_length=200)
    year_established=models.PositiveIntegerField(validators=[MinValueValidator(1500)], null=True)
    hospital_logo=models.ImageField(upload_to="hospital_logo/", null=True, blank=True)
    pic1=models.ImageField(upload_to="hospital_photo/")
    pic2=models.ImageField(upload_to="hospital_photo/", null=True, blank=True)
    pic3=models.ImageField(upload_to="hospital_photo/", null=True, blank=True)
    certificate=models.FileField(upload_to="hospital_certificate/")
    verified = models.CharField(max_length=10, default="No")

    nullable_strings=[about]
    nullable_non_strings=[hospital_logo, pic2, pic3, year_established]

    def save(self, *args, **kwargs):
        for i in self.nullable_non_strings:
            if not i:
                self.i = None
        for i in self.nullable_strings:
            if not i:
                self.i = ""
        super(Hospital, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.hospitalid)

#Hospital will be deleted if its Userid is deleted in UserDetails
class HospitalSpeciality(models.Model):
    hospitalid = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    speciality = models.CharField(max_length=200, blank=False, null=False)
    price = models.PositiveIntegerField(null=True)

    def __str__(self):
        return str(self.hospitalid)+" "+self.speciality

    class Meta:
        unique_together = ('hospitalid', 'speciality')

#Doctor will be deleted if its Userid is deleted in UserDetails
class Doctor(models.Model):
    doctorid = models.OneToOneField(UserDetails, on_delete=models.CASCADE, primary_key=True, related_name="Doctor_set")
    phone=models.PositiveBigIntegerField(validators=[MaxValueValidator(9999999999),MinValueValidator(1000000000)])
    specialization = models.CharField(max_length=100)
    about=models.TextField(max_length=500, blank=True)
    country=models.CharField(max_length=50, blank=True)
    city=models.CharField(max_length=50, blank=True)
    address=models.CharField(max_length=200, blank=True)
    DEFAULT_GENDER='U'
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Trans', 'Trans'),
        (DEFAULT_GENDER, 'Unknown'),
    ]
    gender=models.CharField(max_length=10, choices=GENDER_CHOICES, default=DEFAULT_GENDER)
    experience=models.PositiveSmallIntegerField(validators=[MaxValueValidator(100),MinValueValidator(0)])
    profile_pic=models.ImageField(upload_to="doctor_profile_photo/", blank=True, null=True)
    certificate=models.FileField(upload_to="doctor_certificate/")
    #hospitalid will become null when a hospital is deleted
    hospitalid = models.ForeignKey(Hospital, models.SET_NULL, blank=True, null=True)
    clinic_name = models.CharField(max_length=100, blank=True)
    clinic_photo = models.ImageField(upload_to="clinic_photo/", blank=True, null=True)
    is_independent = models.BooleanField()
    verified = models.CharField(max_length=10, default="No")

    nullable_strings=[about, country, city, address, clinic_name]
    nullable_non_strings=[profile_pic, hospitalid, clinic_photo]

    def save(self, *args, **kwargs):
        for i in self.nullable_non_strings:
            if not i:
                self.i = None
        for i in self.nullable_strings:
            if not i:
                self.i = ""
        super(Doctor, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.doctorid)

#TestingLab will be deleted if its Userid is deleted in UserDetails
class TestingLab(models.Model):
    tlabid = models.OneToOneField(UserDetails, on_delete=models.CASCADE, primary_key=True)
    phone=models.PositiveBigIntegerField(validators=[MaxValueValidator(9999999999),MinValueValidator(1000000000)], null=True)
    about=models.TextField(max_length=2000)
    country=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    fee=models.IntegerField(default=100)
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
class Appointments(models.Model):
   appointmentid = models.AutoField(primary_key=True)
   doctoremail = models.EmailField(max_length=254, blank=False, null=False)
   patientname=models.CharField(max_length=254, blank=False, null=False)
   patientemail = models.EmailField(max_length=254, blank=False, null=False)
   Prescription = models.ImageField(upload_to="Prescriptions/", null=True)
   hospitalemail = models.EmailField(max_length=254,null=True)
   amount_paid = models.PositiveIntegerField()
   appointment_date=models.CharField(max_length=254, blank=False, null=False)
   appointment_time=models.TimeField(blank=False, null=False)
   DEFAULT_MODE_OF_MEETING = 'Remote'
   MEETING_CHOICES = [
       ('Online', 'Online'),
       ('Remote', 'Remote'),
   ]
   mode_of_meeting = models.CharField(max_length=10, choices=MEETING_CHOICES, default=DEFAULT_MODE_OF_MEETING)
   meeting_url=models.CharField(max_length=300,unique=True,null=True)
#     etc... complete according to requirements

class Appointment_slots(models.Model):
    doctorid=models.ForeignKey(Doctor, models.SET_NULL, blank=True, null=True)
    date=models.DateTimeField()
    Slots_Booked=models.IntegerField(default=0)

