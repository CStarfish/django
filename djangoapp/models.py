from django.db import models
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from PIL import Image, ImageOps

import requests

#import your models here
class PoliticalParty(models.Model):
    political_party_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    member_count = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'Political party'

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, date_of_birth, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = self.normalize_email(email),
            date_of_birth = date_of_birth
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    #creates admin user
    def create_superuser(self, first_name, last_name, username, email, date_of_birth, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            first_name,
            last_name,
            username,
            email,
            date_of_birth,
            password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    Custom User model, custom defined to use email as user login and
    also requires a username, first name, last name, and date of birth.
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
    )
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_official = models.BooleanField(default=False)
    is_candidate = models.BooleanField(default=False)
    is_election_office = models.BooleanField(default=False)
    political_party = models.ForeignKey(
        PoliticalParty,
        on_delete = models.DO_NOTHING,
        null = True,
        blank = True,
        related_name = 'members'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'date_of_birth']

    class Meta:
        db_table = 'User'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    @property
    def is_a_student(self):
        "Is the user a student?"
        return self.is_student
    
    @property
    def is_a_official(self):
        "Is the user an official?"
        return self.is_official


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name='profile'
    )
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField(default='')

    class Meta:
        db_table = 'Profile'

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    # resizing images
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.profile_picture.path)

        if img.height > 150 or img.width > 150:
            new_img = (150, 150)
            img.thumbnail(new_img)
            img.save(self.profile_picture.path, format='JPEG')  # Specify the format if needed
        elif img.height < 150 or img.width < 150:
            img = Image.open(self.profile_picture.path)
            img.thumbnail((150, 150), Image.LANCZOS)
            new_img = Image.new('RGB', (150, 150), (255, 255, 255))  # White background
            new_img.paste(img, ((150 - img.width) // 2, (150 - img.height) // 2))  # Center the image
            new_img.save(self.profile_picture.path, format='JPEG')  # Specify the format if needed



class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        primary_key = True
    )
    student_id = models.CharField(max_length=8, null=True, blank=True)
    school_name = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        db_table = 'Student'

    def __str__(self):
        return f"Student: {self.user}"


class Official(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        primary_key = True
    )
    state = models.CharField(max_length=45)

    class Meta:
        db_table = 'Official'

    def __str__(self):
        return f"Official: {self.user}"


class Candidate(models.Model):
    user = models.OneToOneField(
        Official,
        on_delete = models.CASCADE,
        primary_key = True
    )
    campaign_name = models.TextField(default='')
    campaign_details = models.TextField(default='')
    date_applied = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        db_table = 'Candidate'

    def __str__(self):
        return f"Candidate: {self.user.user.first_name} {self.user.user.last_name}"#f"Candidate: {self.official}"


class Policy(models.Model):
    policy_id = models.AutoField(primary_key=True)
    official = models.ForeignKey(
        Official,
        on_delete = models.CASCADE,
        related_name = 'policies'
    )
    name = models.CharField(max_length=45)
    desc = models.TextField(default = '')

    class Meta:
        db_table = 'Policy'

    def __str__(self):
        return self.name


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    official = models.ForeignKey(
        Official,
        on_delete = models.CASCADE,
        related_name ='events'
    )
    name = models.CharField(max_length=45, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    official_count = models.IntegerField(null=True, blank=True, default=0)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    desc = models.TextField(default='')

    class Meta:
        db_table = 'Event'

    def __str__(self):
        return self.name or f"Event {self.event_id}"
    
    def save(self, *args, **kwargs):
        if self.location:
            try:
                # Pass location field in polling location model to the Mapbox API
                response = requests.get(
                    'https://api.mapbox.com/geocoding/v5/mapbox.places/{0}.json'.format(self.location),
                    params={'access_token': 'pk.eyJ1IjoiY3N0YXJmaXNoIiwiYSI6ImNtM2NoaGowNjF3eXAyanB2YWxzdGllYnkifQ.MvqoAPfRiClHv6MGn5TCFA'}
                )
                if response.status_code == 200:
                    data = response.json()

                    # if the geocoding results have features, get the first result
                    if data['features']:
                        coordinates = data['features'][0]['geometry']['coordinates']
                        self.longitude = coordinates[0]
                        self.latitude = coordinates[1]
                    else:
                        print(f"No geocoding results for {self.location}")
                else:
                    print(f"Mapbox geocoding request failed: {response.status_code}")
            except Exception as e:
                print(f"Error fetching coordinates: {e}")

        super().save(*args, **kwargs)

#TO DO: Allow admin access to create election offices
class ElectionOffice(models.Model):
    user = models.OneToOneField(
        Official,
        on_delete = models.CASCADE,
        primary_key = True
    )
    name = models.CharField(max_length=90, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    approved = models.BooleanField(default=False)

    class Meta:
        db_table = 'Election Office'

    def __str__(self):
        return self.location or f"Election Office {self.user.user.username}"
    
    def save(self, *args, **kwargs):
        if self.location:
            try:
                # Pass location field in polling location model to the Mapbox API
                response = requests.get(
                    'https://api.mapbox.com/geocoding/v5/mapbox.places/{0}.json'.format(self.location),
                    params={'access_token': 'pk.eyJ1IjoiY3N0YXJmaXNoIiwiYSI6ImNtM2NoaGowNjF3eXAyanB2YWxzdGllYnkifQ.MvqoAPfRiClHv6MGn5TCFA'}
                )
                if response.status_code == 200:
                    data = response.json()

                    # if the geocoding results have features, get the first result
                    if data['features']:
                        coordinates = data['features'][0]['geometry']['coordinates']
                        self.longitude = coordinates[0]
                        self.latitude = coordinates[1]
                    else:
                        print(f"No geocoding results for {self.location}")
                else:
                    print(f"Mapbox geocoding request failed: {response.status_code}")
            except Exception as e:
                print(f"Error fetching coordinates: {e}")

        super().save(*args, **kwargs)
    

class PollingLocation(models.Model):
    polling_location_id = models.AutoField(primary_key=True)
    office = models.ForeignKey(
        ElectionOffice,
        on_delete = models.DO_NOTHING,
        related_name = 'polling_location'
    )
    name = models.CharField(max_length=90, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact_info = models.CharField(max_length=255, null=True, blank=True)
    location_picture = models.ImageField(default='default.jpg', upload_to='polling_location_images')

    class Meta:
        db_table = 'Polling Location'

    def __str__(self):
        return self
    
    # resizing images taken from profile
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.location_picture.path)

        if self.location:
            try:
                # Pass location field in polling location model to the Mapbox API
                response = requests.get(
                    'https://api.mapbox.com/geocoding/v5/mapbox.places/{0}.json'.format(self.location),
                    params={'access_token': 'pk.eyJ1IjoiY3N0YXJmaXNoIiwiYSI6ImNtM2NoaGowNjF3eXAyanB2YWxzdGllYnkifQ.MvqoAPfRiClHv6MGn5TCFA'}
                )
                if response.status_code == 200:
                    data = response.json()

                    # if the geocoding results have features, get the first result
                    if data['features']:
                        coordinates = data['features'][0]['geometry']['coordinates']
                        self.longitude = coordinates[0]
                        self.latitude = coordinates[1]
                    else:
                        print(f"No geocoding results for {self.location}")
                else:
                    print(f"Mapbox geocoding request failed: {response.status_code}")
            except Exception as e:
                print(f"Error fetching coordinates: {e}")

        super().save(*args, **kwargs)


class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(
        Candidate,
        on_delete = models.DO_NOTHING,
        related_name = 'ratings'
    )
    user = models.ForeignKey(
        User,
        on_delete = models.DO_NOTHING,
        related_name ='ratings'
    )
    rating = models.IntegerField(null=True, blank=True)
    desc = models.TextField(default='')

    class Meta:
        db_table = 'Rating'

    def __str__(self):
        return f"Rating {self.rating} by {self.user} for {self.candidate}"


class Messages(models.Model):
    message_id = models.AutoField(primary_key=True)
    user1 = models.ForeignKey(
        User,
        on_delete = models.DO_NOTHING,
        related_name ='messages_sent'
    )
    user2 = models.ForeignKey(
        User,
        on_delete = models.DO_NOTHING,
        related_name ='messages_received'
    )
    message = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'Messages'

    def __str__(self):
        return f"Message from {self.user1} to {self.user2} at {self.date_created}"
    
class Follow(models.Model):
    #
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follows'
    )
    
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    
    date_followed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Follow'
        unique_together = ('user','candidate','event')
        
    def __str__(self):
        return f"{self.user.username} follows {self.candidate or self.event}"
    

# store updates related to candidates or events
class Update(models.Model):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='updates'
    )
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='updates'
    )
    
    title = models.CharField(max_length=150)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "Update"
    
    def __str__(self):
        return f"Update: {self.title} for {self.candidate or self.event}"
    

class UserUpdate(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_updates'
    )
    
    update = models.ForeignKey(
        Update,
        on_delete=models.CASCADE,
        related_name='user_updates'
    )
    
    read = models.BooleanField(default=False)
    
    date_received = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'UserUpdate'
        
    def __str__(self):
        return f"Update for {self.user.username} : {self.update.title}"
