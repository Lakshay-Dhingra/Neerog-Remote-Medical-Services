from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Username and password will be in default User Model Provided by django
# Create your models here.
class UserDetails(models.Model):
    username=models.CharField(primary_key=True, max_length=50)
    firstname=models.CharField(max_length=100)
    lastname=models.CharField(max_length=100)
    email=models.EmailField(max_length=254, unique=True)
    
    phone=models.PositiveBigIntegerField(validators=[MaxValueValidator(9999999999),MinValueValidator(1000000000)], unique=True)

    country=models.CharField(max_length=100, null=True, blank=False)
    city=models.CharField(max_length=100, null=True, blank=False)

    USER_TYPE_DEFAULT='Fitness Enthusiast'
    USER_TYPE_CHOICES = [
        (USER_TYPE_DEFAULT, 'Fitness Enthusiast'),
        ('Fitness Intstructor', 'Fitness Intstructor'),
        ('Fitness Blogger', 'Fitness Blogger'),
        ('Yoga Intstructor', 'Yoga Intstructor'),
        ('Nutritionist', 'Nutritionist'),
        ('Physiotherapist', 'Physiotherapist'),
        ('Psychologist', 'Psychologist'),
        ('Ayurvedic Doctor', 'Ayurvedic Doctor'),
        ('Other Specialized Doctor', 'Other Specialized Doctor'),
    ]
    user_type=models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default=USER_TYPE_DEFAULT)
    
    DEFAULT_GENDER='U'
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Others'),
        (DEFAULT_GENDER, 'Unknown'),
    ]
    gender=models.CharField(max_length=1, choices=GENDER_CHOICES, default=DEFAULT_GENDER)
    
    age=models.PositiveSmallIntegerField(validators=[MaxValueValidator(150),MinValueValidator(5)], null=True)

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

    DEFAULT_RACE='U'
    RACE_CHOICES = [
        ('American Indian or Alaska Native', 'American Indian or Alaska Native'),
        ('Asian', 'Asian'),
        ('Black or African American', 'Black or African American'),
        ('White or Caucasian', 'White or Caucasian'),
        ('Hispanic or Latino', 'Hispanic or Latino'),
        ('Native Hawaiian or Other Pacific Islander', 'Native Hawaiian or Other Pacific Islander'),
        (DEFAULT_RACE, 'Unknown'),
    ]
    race=models.CharField(max_length=100, choices=RACE_CHOICES, default=DEFAULT_RACE)

    height=models.FloatField(validators=[MaxValueValidator(120),MinValueValidator(20)], null=True)
    weight=models.FloatField(validators=[MaxValueValidator(250),MinValueValidator(5)], null=True)

    profile_pic=models.ImageField(upload_to="profile_pics/", null=True)

    created_at=models.DateTimeField(auto_now=True)

    total_points=models.IntegerField(default=100)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural='User Details'

