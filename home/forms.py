from django import forms


class HomeForm(forms.Form):
    subject_name = forms.CharField(label='과목명', max_length=100, required=False)
    grade = forms.ChoiceField(label='성적', required=False, choices=[
        ('A+', 'A+'),
        ('A0', 'A0'),
        ('B+', 'B+'),
        ('B0', 'B0'),
        ('C+', 'C+'),
        ('C0', 'C0'),
        ('D+', 'D+'),
        ('D0', 'D0'),
        ('F', 'F'),
    ])
    credit = forms.IntegerField(label='학점', required=False)
    course = forms.ChoiceField(label='전공', required=False, choices=[
        ('전핵', '전핵'),
        ('전필', '전필'),
        ('전핵', '전핵'),
        ('전선', '전선'),
        ('중핵', '중핵'),
        ('기교', '기교'),
        ('소교', '소교'),
        ('전공기', '전공기'),
        ('교필', '교필'),
        ('선교', '선교'),
    ])


class StudentInfoForm(forms.Form):
    student_id = forms.IntegerField(label='학번', required=True)
    student_name = forms.CharField(label='이름', max_length=100)
    student_major = forms.ChoiceField(label='전공', choices=[
        ('컴퓨터 학부', '컴퓨터 학부'),
        ('컴퓨터 SW', '컴퓨터 SW'),
        ('미디어 SW', '미디어 SW'),
    ])

    student_semester = forms.ChoiceField(label='학기', choices=[
        ('1-1', '1-1'),
        ('1-2', '1-2'),
        ('2-1', '2-1'),
        ('2-2', '2-2'),
        ('3-1', '3-1'),
        ('3-2', '3-2'),
        ('4-1', '4-1'),
        ('4-2', '4-2')
    ])


class CalculatorForm(forms.Form):
    subject_name = forms.CharField(label='과목명', max_length=100, required=False)
    grade = forms.ChoiceField(label='성적', required=False, choices=[
        ('A+', 'A+'),
        ('A0', 'A0'),
        ('B+', 'B+'),
        ('B0', 'B0'),
        ('C+', 'C+'),
        ('C0', 'C0'),
        ('D+', 'D+'),
        ('D0', 'D0'),
        ('F', 'F'),
    ])
    credit = forms.IntegerField(label='학점', required=False)
    course = forms.ChoiceField(label='전공', required=False, choices=[
        ('전핵', '전핵'),
        ('전필', '전필'),
        ('전핵', '전핵'),
        ('전선', '전선'),
        ('중핵', '중핵'),
        ('기교', '기교'),
        ('소교', '소교'),
        ('전공기', '전공기'),
        ('교필', '교필'),
        ('선교', '선교'),
    ])


class InfoCheckForm(forms.Form):
    student_id = forms.IntegerField(label='학번', required=False)
    student_name = forms.CharField(label='이름', max_length=100, required=False)
    info_semester = forms.ChoiceField(label='학기', required=False, choices=[
        ('1-1', '1-1'),
        ('1-2', '1-2'),
        ('2-1', '2-1'),
        ('2-2', '2-2'),
        ('3-1', '3-1'),
        ('3-2', '3-2'),
        ('4-1', '4-1'),
        ('4-2', '4-2')
        ])


class AcademicStatusForm(forms.Form):
    student_id = forms.IntegerField(label='학번', required=True)
    student_name = forms.CharField(label='이름', max_length=100)
