from django.db import models

# Create your models here.


class Student(models.Model):
    student_id = models.IntegerField(primary_key=True)
    student_name = models.CharField(max_length=100)
    student_major = models.CharField(max_length=100)

    class Meta:
        db_table = 'home_student'


class Semester(models.Model):
    semester_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = 'home_semester'
        unique_together = ('student_id', 'semester')


class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject_semester = models.CharField(max_length=10)
    subject_name = models.CharField(max_length=100)
    grade = models.CharField(max_length=100)
    credit = models.IntegerField()
    course = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    def convert_score(self):
        if self.grade == 'A+':
            return 4.5
        elif self.grade == 'A0':
            return 4.0
        elif self.grade == 'B+':
            return 3.5
        elif self.grade == 'B0':
            return 3.0
        elif self.grade == 'C+':
            return 2.5
        elif self.grade == 'C0':
            return 2.0
        elif self.grade == 'D+':
            return 1.5
        elif self.grade == 'D0':
            return 1.0
        elif self.grade == 'F':
            return 0.0

    class Meta:
        db_table = 'home_subject'


class Gpa_avg(models.Model):
    gpa_avg_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10)
    gpa_avg = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    major_gpa_avg = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    semester_credit = models.IntegerField(default=0)

    class Meta:
        db_table = 'home_gpa_avg'


class Academic_status(models.Model):
    status_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    total_gpa_avg = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    total_major_gpa_avg = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    total_semester = models.IntegerField(default=0)

    class Meta:
        db_table = 'home_academic_status'


class Graduation_condition(models.Model):
    condition_id = models.AutoField(primary_key=True)
    total_credit = models.IntegerField(default=130)
    total_semester = models.IntegerField(default=8)
    gpa_avg = models.BooleanField(default=True)
    graduation_project = models.BooleanField(default=False)
    important_main = models.IntegerField(default=2)
    basic_elective = models.IntegerField(default=10)
    choice_elective = models.IntegerField(default=15)
    choice_elective_part = models.IntegerField(default=7)
    knowledge_education = models.IntegerField(default=1)
    major_basic_elective = models.IntegerField(default=4)
    major_essential = models.IntegerField(default=27)
    major_choice = models.IntegerField(default=48)
    common_elective = models.IntegerField(default=12)

    class Meta:
        db_table = 'home_graduation_condition'
