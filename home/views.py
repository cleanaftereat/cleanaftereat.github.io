from django.shortcuts import render, redirect, get_object_or_404
from django.forms.formsets import formset_factory
from django.db.models import Avg, Sum, Q
from .forms import HomeForm, StudentInfoForm, CalculatorForm, InfoCheckForm, AcademicStatusForm
from .models import Student, Semester, Subject, Gpa_avg, Academic_status, Graduation_condition
import matplotlib.pyplot as plt
from io import BytesIO
import base64


def about(request):
    return render(request, 'about.html', {})
def home(request):
    Homeformset = formset_factory(HomeForm, extra=10)
    total_credit = 0
    total_score = 0
    total_major_credit = 0
    total_major_score = 0

    if request.method == 'POST':
        formset = Homeformset(request.POST)
        if formset.is_valid():
            for form in formset:
                subject_name = form.cleaned_data.get('subject_name')
                grade = form.cleaned_data.get('grade')
                credit = form.cleaned_data.get('credit')
                course = form.cleaned_data.get('course')

                if subject_name and credit is not None:
                    converted_score = convert_score(grade)
                    total_credit += credit
                    total_score += credit * converted_score
                    if course == '전핵' or course == '전선' or course == '전필' or course == '전공기':
                        total_major_credit += credit
                        total_major_score += credit * converted_score
            if total_credit:
                total_score = round(total_score / total_credit, 2)
            if total_major_credit:
                total_major_score = round(total_major_score / total_major_credit, 2)

    else:
        formset = Homeformset()
    return render(request, 'home.html', {
        'formset': formset,
        'total_credit': total_credit,
        'total_score': total_score,
        'total_major_credit': total_major_credit,
        'total_major_score': total_major_score
    })


def student_info(request):
    if request.method == 'POST':
        form = StudentInfoForm(request.POST)
        if form.is_valid():
            student_data = form.cleaned_data

            student, created = Student.objects.get_or_create(
                student_id=student_data['student_id'],
                defaults={
                    'student_name': student_data['student_name'],
                    'student_major': student_data['student_major'],
                }
            )

            semester, created_semester = Semester.objects.get_or_create(
                student_id=student,
                semester=student_data['student_semester'],
                defaults={'semester': student_data['student_semester']}
            )

            if not created:
                student.student_name = student_data['student_name']
                student.student_major = student_data['student_major']
                student.save()

            if not created_semester:
                semester.semester = student_data['student_semester']
                semester.save()

            request.session['student_id'] = student.student_id
            request.session['student_semester'] = semester.semester

            return redirect('calculator')
    else:
        form = StudentInfoForm()
    return render(request, 'student_info_form.html', {'form': form})


def convert_score(grade):
        if grade == 'A+':
            return 4.5
        elif grade == 'A0':
            return 4.0
        elif grade == 'B+':
            return 3.5
        elif grade == 'B0':
            return 3.0
        elif grade == 'C+':
            return 2.5
        elif grade == 'C0':
            return 2.0
        elif grade == 'D+':
            return 1.5
        elif grade == 'D0':
            return 1.0
        elif grade == 'F':
            return 0.0


def calculate_score(student_id, subject_semester):
    subjects = Subject.objects.filter(student_id=student_id, subject_semester=subject_semester)
    total_credit = 0
    total_score = 0
    total_major_credit = 0
    total_major_score = 0

    for subject in subjects:
        if subject.credit is not None:
            total_credit += subject.credit
            total_score += subject.convert_score() * subject.credit
            if subject.course == '전핵' or subject.course == '전선' or subject.course == '전필' or subject.course == '전공기':
                total_major_credit += subject.credit
                total_major_score += subject.convert_score() * subject.credit

    average_score = round(total_score / max(total_credit, 1), 2)
    average_major_score = round(total_major_score / max(total_major_credit, 1), 2)

    return average_score, average_major_score, total_credit


def calculator(request):
    CalculatorFormSet = formset_factory(CalculatorForm, extra=10)
    student_id = request.session.get('student_id')
    subject_semester = request.session.get('student_semester')
    average_score = 0.00
    average_major_score = 0.00

    if request.method == 'POST':
        formset = CalculatorFormSet(request.POST)
        if formset.is_valid():
            student = Student.objects.get(student_id=student_id)

            for form in formset:
                subject_name = form.cleaned_data.get('subject_name')
                grade = form.cleaned_data.get('grade')
                credit = form.cleaned_data.get('credit')
                course = form.cleaned_data.get('course')

                if subject_name and grade and credit and course:
                    existing_subject = Subject.objects.filter(
                        student_id=student,
                        subject_semester=subject_semester,
                        subject_name=subject_name,
                        course=course
                    ).first()

                    if existing_subject:
                        existing_subject.grade = grade
                        existing_subject.credit = credit
                        existing_subject.score = existing_subject.convert_score()
                        existing_subject.save()
                    else:
                        subject = Subject(
                            student_id=student,
                            subject_semester=subject_semester,
                            subject_name=subject_name,
                            grade=grade,
                            credit=credit,
                            course=course,
                        )
                        subject.score = subject.convert_score()
                        subject.save()

            average_score, average_major_score, total_credit = calculate_score(student, subject_semester)

            gpa_avg, created = Gpa_avg.objects.get_or_create(
                student=student,
                semester=subject_semester,
                defaults={
                    'gpa_avg': average_score,
                    'major_gpa_avg': average_major_score,
                    'semester_credit': total_credit,
                }
            )

            if not created:
                gpa_avg.gpa_avg = average_score
                gpa_avg.major_gpa_avg = average_major_score
                gpa_avg.semester_credit = total_credit
                gpa_avg.save()

            del request.session['student_id']
            del request.session['student_semester']

    else:
        formset = CalculatorFormSet()

    return render(request, 'calculator.html', {'formset': formset, 'average_score': average_score, 'average_major_score': average_major_score})


def info_check(request):
    sub_info_list = []
    gpa_avg = 0.00
    major_gpa_avg = 0.00
    total_credit = 0

    if request.method == 'POST':
        form = InfoCheckForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            info_semester = form.cleaned_data['info_semester']

            subject_info_list = Subject.objects.filter(student_id=student_id, subject_semester=info_semester)

            if 'selected_subjects' in request.POST:
                selected_subjects = request.POST.getlist('selected_subjects')
                selected_subjects = [int(subject_id) for subject_id in selected_subjects if subject_id.isdigit()]
                if selected_subjects:
                    first_subject = Subject.objects.filter(subject_id__in=selected_subjects).first()
                if first_subject:
                    student_id = first_subject.student_id_id
                    semester = first_subject.subject_semester
                    Subject.objects.filter(subject_id__in=selected_subjects).delete()
                    update_gpa_avg(student_id, semester)

            for subject_info in subject_info_list:
                sub_info = {
                    'subject_id': subject_info.subject_id,
                    'sub_name': subject_info.subject_name,
                    'sub_grade': subject_info.grade,
                    'sub_credit': subject_info.credit,
                    'sub_course': subject_info.course
                }
                sub_info_list.append(sub_info)

            avg_scores = Gpa_avg.objects.filter(student_id=student_id, semester=info_semester)
            if avg_scores.exists():
                avg_score = avg_scores.first()
                gpa_avg = avg_score.gpa_avg
                major_gpa_avg = avg_score.major_gpa_avg
                total_credit = avg_score.semester_credit

    else:
        form = InfoCheckForm()

    return render(request, 'info_check.html', {'form': form, 'sub_info_list': sub_info_list, 'gpa_avg': gpa_avg, 'major_gpa_avg': major_gpa_avg, 'total_credit': total_credit})


def update_gpa_avg(student_id, semester):
    major_condition = Q(course='전핵') | Q(course='전필') | Q(course='전선') | Q(course='전공기')
    student = Student.objects.get(student_id=student_id)
    avg_data = Subject.objects.filter(student_id=student_id, subject_semester=semester).aggregate(
        gpa_avg=Avg('score'),
        major_gpa_avg=Avg('score', filter=major_condition),
        semester_credit=Sum('credit')
    )

    Gpa_avg.objects.update_or_create(
        student=student,
        semester=semester,
        defaults={
            'gpa_avg': avg_data['gpa_avg'] or 0.00,
            'major_gpa_avg': avg_data['major_gpa_avg'] or 0.00,
            'semester_credit': avg_data['semester_credit'] or 0
        }
    )
    update_academic_status(student_id)


def update_academic_status(student_id):
    avg_score = 0.00
    major_avg_score = 0.00
    total_credit = 0
    count = 0

    student = Student.objects.get(student_id=student_id)
    semesters = Semester.objects.filter(student_id=student_id)
    semester = semesters.first()

    if student:
        if semester:
            for semester in semesters:
                gpa_avg = Gpa_avg.objects.get(student_id=student, semester=semester)
                avg_score.append(gpa_avg.gpa_avg)
                major_avg_score.append(gpa_avg.major_gpa_avg)
                total_credit += gpa_avg.semester_credit
                count += 1

                if count > 0:
                    avg_score = Avg(avg_score)
                    major_avg_score = Avg(major_avg_score)

                status = Academic_status(
                    student_id=student,
                    total_gpa_avg=avg_score,
                    total_major_gpa_avg=major_avg_score,
                    total_semester=total_credit
                )
                status.save()


elective_part_1 = [
    '교양한국어초급',
    '교양한국어중급',
    '한국어의이해',
    '일본어Level1',
    '일본어Level2',
    '기초한국어이해',
    '중국어Level1',
    '중국어Level2',
    '교양프랑스어',
    '여행프랑스어',
    'start 독일어',
    'easy 독일어',
    'start 러시아어',
    'easy 러시아어',
    '글로벌교양1',
    '글로벌리더십을위한외국어학습방법',
    '통역과번역의이해',
    'ALL that English Basic',
    'ALL that English1',
    'ALL that English Speaking1',
    'ALL that English2',
    'ALL that English3',
    'ALL that English Speaking2',
    '세계와통번역',
    '실무한중통번역연습',
    '여행영어와세계',
    '관광통역중국어'
]
elective_part_2 = [
    '유럽통합의이해',
    '현대사회와미국문화',
    '유럽의문화적전통',
    '종교와21세기',
    '유럽문화와사회',
    '한중문화비교',
    '문학으로읽는세상',
    '중앙아시아의이해',
    '문화콘텐츠의이해와비평',
    '북유럽의이해',
    '미디어와인간관계',
    '글로벌교양2',
    '대중문화로이해하는중국',
    '라틴어의이해와로마문명',
    '세계의축제와여행',
    '세계차(tea)산업의이해',
    '시베리아횡단열차와도시',
    '식문화의형성과세계화',
    '유럽도시브랜딩',
    '인간지성과소통:논쟁과협상',
    '일본사회의이해',
    '중세영국과프랑스의문화교류사',
    '지성인의자아혁신과리더쉽',
    '프랑스문화로읽는문화산업',
    '한국문학읽기와영화읽기',
    '현대사회와감성사고력',
    '문화컨텐츠산업의이해',
    '창의적콘텐츠와명품브랜딩론',
    '국제사회문화의이해',
    '4차산업혁명과미래',
    '대중연설의역사와이론',
    '문화기술과디지털콘텐츠',
    '음식문화로이해하는중국',
    '세계언어의이해',
    '고대문명과고고학',
    '중국도시랜선여행'
]
elective_part_3 = [
    '결혼과가족',
    '법과현대생활',
    '사회학의이해',
    '한국경제의이해',
    '한국민족운동사의인식',
    '한국정치의분석',
    '현대관광여가론',
    '현대사회와매스컴',
    '한반도와국제정치',
    '북한사회의이해',
    '성과사랑',
    '동아시아역사속의전쟁과평화',
    '한국사인물전',
    '20세기한국사',
    '문화로보는서양의역사',
    '경제,경영과삶',
    '광고홍보의이해와실제',
    '글로벌교양3',
    '금융의이해',
    '디지털사회의마케팅',
    '산업사회의이해',
    '설득커뮤니케이션',
    '여성과법률',
    '이미지로역사읽기',
    '정보사회와경영',
    '조직속의심리학',
    '창업마케팅',
    '한국소방의역사',
    '한국행정의이해',
    '현대중국사회의이해',
    '스타트업아이디어와가치창출',
    '사회적경제와소셜벤처',
    '조직과리더십',
    '스타트업과비즈니스모델',
    '신문과사회트렌드분석론',
    'STARTUP BUSINESSPLAN',
    '격변의동북아시아와한국사',
    '국제개발협력입문',
    '국제마케팅전략입문',
    '동서문화교류사',
    '동양문화사',
    '러시아역사와사회의이해',
    '발달주기와생애설계',
    '법의사유적접근',
    '벤처스타트업',
    '벤처창업의이해',
    '생활과금융',
    '생활속의경제경영론',
    '영상역사학',
    '한국사의재조명',
    '현대사회의창업과리더십',
    '화성의문화와역사',
    '미디어로보는교육',
    '한국의세계문화유산',
    '글로벌비즈니스에티켓&매너',
    '세계체제의이해',
    '융합적사고의기초',
    '자기개발과청년창업'
]
elective_part_4 = [
    '러시아명작의이해',
    '러시아문화',
    '문화인류학',
    '언어와문화',
    '인간과윤리',
    '프랑스문학과미술',
    '만화와철학',
    '성과철학',
    '박물관문화콘텐츠',
    '무의식과마음의대화',
    '인간심리의분석',
    '생각의탄생1(서양편)',
    '생각의탄생2(동양편)',
    '이야기와치유의철학',
    '디아스포라문학과영화',
    '명심보감의현대적이해',
    '문학과스토리텔링',
    '문예창작의이론과실제',
    '중국신화의세계',
    '서양문학의이해',
    '문화와정치',
    '동유럽의사회와문화',
    '예술에나타난종교와철학',
    '글로벌교양4',
    '대학과인간',
    '명화로스토리텔링하기',
    '문학철학의이해',
    '문화와사상',
    '신화와철학',
    '신화의이해',
    '영어권문학과문화',
    '논어의현대적이해',
    '대학생을위한한자와고사성어',
    '러시아히스토리와컬처',
    '영상언어의이해',
    '특수교육의이해',
    '현대시이해와감상',
    '아동심리의이해',
    '미디어문학과상상력',
    '문화간커뮤니케이션의이론과응용'
]
elective_part_5 = [
    '발명과특허',
    '디지털리터러시',
    'MOS1',
    '가상현실의이해',
    '글로벌교양5',
    '데이터와코딩의이해',
    '드론의활용과이해',
    '아이디어와발명',
    '엑셀과R을활용한응용통계',
    '인공지능개념과원리',
    '재난의과학적이해',
    '정보화사회와뉴미디어',
    '파이썬프로그래밍이해',
    '피지컬컴퓨팅',
    '컴퓨터적사고와코딩',
    'Startup빅데이터입문',
    '기술사업화이해',
    '메이커소양',
    '컴퓨터언어개론',
    'MOS2',
    'Google G-Suite활용과 이해',
    '클라우드컴퓨팅의이해',
    'JAVA프로그래밍입문',
    'Startup웹프로그래밍',
    'Startup인공지능코딩',
    'VR애니메이션세계',
    '데이터베이스언어SQL입문',
    '리눅스입문',
    '마인크래프트로배우는파이썬',
    '메이커스페이스스타트업입문',
    '제품개발프로세스',
    '지식재산개론',
    '4차산업혁명미래기술과Startup'
]
elective_part_6 = [
    '전통예술의이해',
    '창의프로젝트',
    '4차산업과스포츠',
    '4차산업혁명과음악',
    '글로벌교양6',
    '다이어트와체형관리',
    '매체와대중예술이해와감상',
    '무대예술의이해와감상',
    '미디어아트와현대산업과사회',
    '미술로해석하는도시건축과자연환경',
    '생애주기건강관리',
    '세계연극이야기',
    '세계영화이야기',
    '식생활과영양',
    '실용음악과공연예술',
    '영화와여성이미지',
    '예술과심리치료',
    '외국무용예술의이해',
    '우리연극이야기',
    '응급처치와안전',
    '지역사회와봉사',
    '창의적드라마와놀이',
    '한국무용예술의이해',
    '한국영화로보는세상',
    '현대생활과스포츠',
    '허브식물학',
    '레저스포츠의이해와실제',
    '대중문화속의클래식',
    '대학합창클래스',
    '라켓스포츠의이론과실제',
    '뮤지컬과움직임',
    '미술과인문학',
    '생활구기의이론과실제',
    '요가와다이어트',
    '클래식음악과오페라',
    '한국음악의이해와감상',
    '일.사랑.행복',
    '세계명작의감상'
]
elective_part_7 = [
    '인간과우주',
    '자연과학의이해',
    '화학의이해',
    '환경과학',
    '신화와과학',
    '과학문명사',
    '생활속의과학원리',
    '과학의재발견',
    '과학의철학적이해',
    '글로벌교양7',
    '생명공학의이해',
    '예체능속의과학원리',
    '자연의언어',
    '과학발달의역사',
    '특허출원도전하기',
    '인간과우주',
    '자연과학의이해',
    '화학의이해',
    '환경과학',
    '신화와과학',
    '과학문명사',
    '생활속의과학원리',
    '과학의재발견',
    '과학의철학적이해',
    '글로벌교양7',
    '생명공학의이해',
    '예체능속의과학원리',
    '자연의언어',
    '과학발달의역사',
    '특허출원도전하기'
]


def calculate_graduation_condition(student_id):
    count = 0
    elective_parts = [1, 2, 3, 4, 5, 6, 7]
    left_credit = 0
    left_semester = 0
    gpa_criterion = True
    project_criterion = False
    left_important_main = 0
    left_basic_elective = 0
    left_choice_elective = 0
    left_choice_elective_part = elective_parts
    left_knowledge_education = 0
    left_major_basic_elective = 0
    left_major_essential = 0
    left_major_choice = 0
    left_common_elective = 0

    graduation_condition = Graduation_condition.objects.create()

    student = Student.objects.get(student_id=student_id)
    semesters = Semester.objects.filter(student_id=student_id)
    semester = semesters.first()

    if student:
        if semester:
            for semester in semesters:
                gpa_avg = Gpa_avg.objects.get(student=student_id, semester=semester.semester)
                count += 1
                if gpa_avg.gpa_avg <= 2.00:
                    graduation_condition.gpa_avg = False
                graduation_condition.total_credit -= gpa_avg.semester_credit
                graduation_condition.total_semester -= 1

                subjects = Subject.objects.filter(student_id=student_id, subject_semester=semester.semester)
                subject = subjects.first()
                if graduation_condition:
                    if subject:
                        for subject in subjects:
                            if subject.subject_name == '졸업프로젝트' or subject.subject_name == '졸업 프로젝트':
                                graduation_condition.graduation_project = True
                            if subject.course == '중핵':
                                graduation_condition.important_main -= 1
                            if subject.course == '기교':
                                graduation_condition.basic_elective -= 1
                            if subject.course == '선교':
                                if graduation_condition.choice_elective <= 0:
                                    graduation_condition.common_elective -= 3
                                else:
                                    graduation_condition.choice_elective -= 3
                                    if subject.subject_name in elective_part_1:
                                        graduation_condition.choice_elective_part -= 1
                                        elective_parts.remove(1)
                                    elif subject.subject_name in elective_part_2:
                                        graduation_condition.choice_elective_part -= 1
                                        elective_parts.remove(2)
                                    elif subject.subject_name in elective_part_3:
                                        graduation_condition.choice_elective_part -= 1
                                        elective_parts.remove(3)
                                    elif subject.subject_name in elective_part_4:
                                        graduation_condition.choice_elective_part -= 1
                                        elective_parts.remove(4)
                                    elif subject.subject_name in elective_part_5:
                                        graduation_condition.choice_elective_part -= 1
                                        elective_parts.remove(5)
                                    elif subject.subject_name in elective_part_6:
                                        graduation_condition.choice_elective_part -= 1
                                        elective_parts.remove(6)
                                    elif subject.subject_name in elective_part_7:
                                        graduation_condition.choice_elective_part -= 1
                                        elective_parts.remove(7)
                            if subject.course == '소교':
                                graduation_condition.knowledge_education -= 1
                            if subject.course == '전기교':
                                graduation_condition.major_basic_elective -= 0
                            if subject.course == '전핵':
                                graduation_condition.major_essential -= 3
                            if subject.course == '전선':
                                if graduation_condition.major_choice <= 0:
                                    graduation_condition.common_elective -= 3
                                else:
                                    graduation_condition.major_choice -= 3
            graduation_condition.save()

    left_credit = graduation_condition.total_credit
    left_semester = graduation_condition.total_semester
    gpa_criterion = graduation_condition.gpa_avg
    project_criterion = graduation_condition.graduation_project
    left_important_main = graduation_condition.important_main
    left_basic_elective = graduation_condition.basic_elective
    left_choice_elective = graduation_condition.choice_elective
    left_choice_elective_part = graduation_condition.choice_elective_part
    left_knowledge_education = graduation_condition.knowledge_education
    left_major_basic_elective = graduation_condition.major_basic_elective
    left_major_essential = graduation_condition.major_essential
    left_major_choice = graduation_condition.major_choice
    left_common_elective = graduation_condition.common_elective

    return left_credit, left_semester, gpa_criterion, project_criterion, left_important_main, left_basic_elective, left_choice_elective, left_choice_elective_part, elective_parts, left_knowledge_education, left_major_basic_elective, left_major_essential, left_major_choice, left_common_elective


def academic_status(request):
    avg_score_temp = []
    major_avg_score_temp = []
    avg_score = 0.00
    major_avg_score = 0.00
    total_credit = 0
    count = 0
    elective_parts = [1, 2, 3, 4, 5, 6, 7]
    left_credit = 0
    left_semester = 0
    gpa_criterion = False
    project_criterion = False
    left_important_main = 0
    left_basic_elective = 0
    left_choice_elective = 0
    left_choice_elective_part = elective_parts
    left_knowledge_education = 0
    left_major_basic_elective = 0
    left_major_essential = 0
    left_major_choice = 0
    left_common_elective = 0
    plot_base64 = None
    gpa_crit = '미통과'
    project_crit = '미통과'

    if request.method == 'POST':
        form = AcademicStatusForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            student_name = form.cleaned_data['student_name']

            student = Student.objects.get(student_id=student_id)
            left_credit, left_semester, gpa_criterion, project_criterion, left_important_main, left_basic_elective, left_choice_elective, left_choice_elective_part, elective_parts, left_knowledge_education, left_major_basic_elective, left_major_essential, left_major_choice, left_common_elective = calculate_graduation_condition(student_id)

            semesters = Semester.objects.filter(student_id=student_id)
            semester = semesters.first()
            if student:
                if semester:
                    for semester in semesters:
                        gpa_avg = Gpa_avg.objects.get(student=student, semester=semester.semester)
                        avg_score_temp.append(gpa_avg.gpa_avg)
                        major_avg_score_temp.append(gpa_avg.major_gpa_avg)
                        total_credit += gpa_avg.semester_credit
                        count += 1

                    if count > 0:
                        avg_score = round(sum(avg_score_temp) / len(avg_score_temp), 2)
                        major_avg_score = round(sum(major_avg_score_temp) / (len(major_avg_score_temp) - major_avg_score_temp.count(0.00)), 2)

                    print(major_avg_score_temp)

                    plt.figure(figsize=(8, 4))
                    semesters = range(1, len(avg_score_temp) + 1)
                    width = 0.35

                    plt.bar(semesters, avg_score_temp, width, label='Average Score', alpha=0.7)
                    plt.bar([s + width for s in semesters], major_avg_score_temp, width, label='Major Average Score', alpha=0.7)

                    plt.title('Average Scores Over Semesters')
                    plt.xlabel('Semester')
                    plt.ylabel('Score')
                    plt.legend()

                    plt.xticks([s + width / 2 for s in semesters], [f"{(s - 1) // 2 + 1}-{(s - 1) % 2 + 1}" for s in semesters])
                    plot_img = BytesIO()
                    plt.savefig(plot_img, format='png')
                    plt.close()

                    plot_img.seek(0)
                    plot_base64 = base64.b64encode(plot_img.getvalue()).decode()

                    status = Academic_status(
                        student_id=student,
                        total_gpa_avg=avg_score,
                        total_major_gpa_avg=major_avg_score,
                        total_semester=total_credit
                    )
                    status.save()

                    if gpa_criterion:
                        gpa_crit = '통과'
                    if project_criterion:
                        project_crit = '통과'

    else:
        form = AcademicStatusForm()

    return render(request, 'academic_status.html', {
        'form': form,
        'avg_score': avg_score,
        'major_avg_score': major_avg_score,
        'total_credit': total_credit,
        'left_credit': left_credit,
        'left_semester': left_semester,
        'gpa_crit': gpa_crit,
        'project_crit': project_crit,
        'left_important_main': left_important_main,
        'left_basic_elective': left_basic_elective,
        'left_choice_elective': left_choice_elective,
        'left_choice_elective_part': left_choice_elective_part,
        'elective_parts': elective_parts,
        'left_knowledge_education': left_knowledge_education,
        'left_major_basic_elective': left_major_basic_elective,
        'left_major_essential': left_major_essential,
        'left_major_choice': left_major_choice,
        'left_common_elective': left_common_elective,
        'plot_base64': plot_base64,
        })
