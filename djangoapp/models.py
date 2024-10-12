from django.db import models

#import your models here

class PoliticalParty(models.Model):
    political_party_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    member_count = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'Political party'

    def __str__(self):
        return self.name


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    political_party = models.ForeignKey(
        PoliticalParty,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='users'
    )
    email = models.CharField(max_length=45, null=True, blank=True)
    phone_number = models.CharField(max_length=45, null=True, blank=True)
    firstname = models.CharField(max_length=45, null=True, blank=True)
    lastname = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        db_table = 'User'

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='account'
    )
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)

    class Meta:
        db_table = 'Account'

    def __str__(self):
        return self.username


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student'
    )
    school_id = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        db_table = 'Student'

    def __str__(self):
        return f"Student: {self.user}"


class Official(models.Model):
    official_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='official'
    )
    state = models.CharField(max_length=45)

    class Meta:
        db_table = 'Official'

    def __str__(self):
        return f"Official: {self.user}"


class Candidate(models.Model):
    candidate_id = models.AutoField(primary_key=True)
    official = models.OneToOneField(
        Official,
        on_delete=models.DO_NOTHING,
        related_name='candidate'
    )

    class Meta:
        db_table = 'Candidate'

    def __str__(self):
        return f"Candidate: {self.official}"


class Policy(models.Model):
    policy_id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='policies'
    )
    name = models.CharField(max_length=45)
    desc = models.CharField(max_length=90, null=True, blank=True)

    class Meta:
        db_table = 'Policy'

    def __str__(self):
        return self.name


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='events'
    )
    name = models.CharField(max_length=45, null=True, blank=True)
    location = models.CharField(max_length=90, null=True, blank=True)
    official_count = models.IntegerField(null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'Event'

    def __str__(self):
        return self.name or f"Event {self.event_id}"


class ElectionOffice(models.Model):
    election_office_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name='election_offices'
    )
    location = models.CharField(max_length=90, null=True, blank=True)

    class Meta:
        db_table = 'Election Office'

    def __str__(self):
        return self.location or f"Election Office {self.election_office_id}"


class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.DO_NOTHING,
        related_name='ratings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name='ratings'
    )
    rating = models.IntegerField(null=True, blank=True)
    desc = models.CharField(max_length=90, null=True, blank=True)

    class Meta:
        db_table = 'Rating'

    def __str__(self):
        return f"Rating {self.rating} by {self.user} for {self.candidate}"


class Messages(models.Model):
    message_id = models.AutoField(primary_key=True)
    user1 = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name='messages_sent'
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name='messages_received'
    )
    message = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'Messages'

    def __str__(self):
        return f"Message from {self.user1} to {self.user2} at {self.date_created}"
