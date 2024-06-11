from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm
from django.http import JsonResponse, HttpResponseBadRequest
from .models import SecurityQuestion, CustomUser, CheckedRelation, ResourceInfo
import datetime
import os
import subprocess
import json
import ast

# 장고 프로젝트의 루트 디렉토리 경로. 
# 외부 파이썬 코드를 views.py 내부에서 실행하기 위함.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 회원가입
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'signup.html', {'custom_error': 'is-not-valid'})
    else:
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

# 로그인
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            current_user = request.user
            return redirect('home')
        else:
            return render(request, 'login.html', {'custom_error':'re-enter'})
    else:
        if not request.user.is_authenticated:
            return render(request, 'login.html')
        else:
            return redirect('home')

# 로그아웃
def logout_view(request):
    logout(request)
    return redirect('login')

# 회원탈퇴
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return render(request, 'delete_account.html')

# 메인 페이지 - 대시보드 
def home(request):
    # 로그인하지 않은 상태라면, 로그인 페이지로 리다이렉트
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        # 양호 개수, 검사 완료된 점검 항목의 총 개수를 보안 점검 항목별로 저장함.
        service_good_ratio = {
        "LINUX" : [0, 0],
        "TOMCAT": [0, 0], 
        "NGINX" : [0, 0], 
        "MYSQL" : [0, 0], 
        "DOCKER": [0, 0]
        }

    # 현재 로그인한 유저
    current_user = request.user
    
    # 현재 로그인한 사용자와 관련된 검사 완료된 원격, 상태정보 가져오기
    completed_resources = ResourceInfo.objects.filter(user=current_user, inspection_status='검사완료')

    # 위에서 구한 원격, 상태정보와 관련된 점검사항을 순회하며 
    # 해당 점검사항의 유형에 개수를 카운트한다.(질문 개수 카운트)
    for resource in completed_resources:
        for question in resource.questionList.all():
            matching_question = SecurityQuestion.objects.get(id=question.id)
            # 검사완료된 질문 개수 카운트
            service_good_ratio[matching_question.qType][1] += 1
            try:
                # 관련 검사 결과 데이터를 가져오기 
                checked_relation = CheckedRelation.objects.get(resource=resource, question=matching_question)
                # 결과가 양호이면 양호 개수 1증가
                if checked_relation.result == "양호":
                    service_good_ratio[matching_question.qType][0] += 1
            except CheckedRelation.DoesNotExist:
                print("No Checked Relation Found")

    # service_good_ratio의 값에 양호 비율을 추가한다. 
    for service, ratio in service_good_ratio.items():
        if ratio[1] == 0:
            ratio.append(0)
        else:
            ratio.append((ratio[0] / ratio[1]) * 100)

    return render(request, 'home.html', {'user': current_user, 'service_good_ratio': service_good_ratio})

# 아이디 중복확인 체크 
def check_username(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = CustomUser.objects.get(username=username)
            return JsonResponse({'is_taken': True})
        except CustomUser.DoesNotExist:
            return JsonResponse({'is_taken': False})
    return JsonResponse({}, status=400)


def service_check(request):
    # 원격정보 및 상태정보 생성
    if request.method == 'POST':
        user = request.user
        question_ids = request.POST.getlist('question_id')
        remote_ip = request.POST.get('remote_ip')
        remote_id = request.POST.get('remote_id')
        remote_pw = request.POST.get('remote_pw')
        resource_ip = request.POST.get('resource_ip')
        resource_id = request.POST.get('resource_id')
        resource_pw = request.POST.get('resource_pw')
        info_memo = request.POST.get('info_memo')

        # 기존에 동일한 원격정보 및 상태 정보가 있는지 확인
        existing_resource_info = ResourceInfo.objects.filter(
            remote_ip=remote_ip,
            remote_id=remote_id,
            remote_pw=remote_pw,
            resource_ip=resource_ip,
            resource_id=resource_id,
            resource_pw=resource_pw,
            user=user
        ).first()

        # 만약, 존재하면 새로 생성하지 않는다. 
        if existing_resource_info:
            resource_info = existing_resource_info
        else:
            # 존재하지 않으면 새로 생성한다. 
            resource_info = ResourceInfo.objects.create(
                remote_ip=remote_ip,
                remote_id=remote_id,
                remote_pw=remote_pw,
                resource_ip=resource_ip,
                resource_id=resource_id,
                resource_pw=resource_pw,
                info_memo=info_memo,
                user=user
            )

        # 기존에 관계된 점검사항, 검사결과 정보를 삭제하고, 
        # 상태정보를 검사전으로 바꾼다. 
        resource_info.questionList.clear()
        resource_info.inspection_status = '검사전'
        CheckedRelation.objects.filter(resource=resource_info).delete()
        resource_info.save()

        # 사용자가 선택한 점검사항과 원격 및 상태 정보와 연결짓는다.
        for question_id in question_ids:
            try:
                question = SecurityQuestion.objects.get(id=question_id)
                resource_info.questionList.add(question)
    
            except SecurityQuestion.DoesNotExist:
                return HttpResponseBadRequest("Security question with id {} does not exist".format(question_id))

        return redirect('service-ready')

    else:
        # 점검 서비스를 선택할 때, 유형별 점검사항 데이터가 필요함
        # 점검사항을 유형별로 뿌려주기 위해 데이터 조작 
        linuxQuestionList = SecurityQuestion.objects.filter(qType="LINUX")
        tomcatQuestionList = SecurityQuestion.objects.filter(qType="TOMCAT")
        mysqlQuestionList = SecurityQuestion.objects.filter(qType="MYSQL")
        dockerQuestionList = SecurityQuestion.objects.filter(qType="DOCKER")
        nginxQuestionList = SecurityQuestion.objects.filter(qType="NGINX")

        return render(request, 'service-check.html', {'questionList' : {
            "linux" : linuxQuestionList,
            "tomcat" : tomcatQuestionList,
            "mysql" :  mysqlQuestionList,
            "docker" : dockerQuestionList,
            "nginx" : nginxQuestionList
        }}) 

def service_ready(request):
    # 보안 점검하기 위해 외부 파이썬 코드를 실행
    if request.method == "POST":
        serviceData_id = request.POST.get('serviceData_id')
        serviceData_question_ids = ast.literal_eval(request.POST.get('serviceData_question_ids'))

        # 해당 원격 상태 정보를 가져옴
        resource_info = ResourceInfo.objects.get(id=serviceData_id)
       
        remote_ip = resource_info.remote_ip
        remote_id = resource_info.remote_id
        remote_pw = resource_info.remote_pw

        remote_db_ip = resource_info.resource_ip
        remote_db_id = resource_info.resource_id
        remote_db_pw = resource_info.resource_pw

        # 해당 점검사항 정보를 가져옴 
        security_questions = SecurityQuestion.objects.filter(id__in=serviceData_question_ids)
        
        for question in security_questions:
            # 외부 파이썬 코드 돌리기 
            # 점검사항의 pk 즉, id에 따라 양호, 취약을 구분하는 코드가 다르기 때문에
            # 점검사항의 id가 필요하다.
            # 또한, ssh 원격접속 시 필요한 ip, id, pw도 같이 보내준다. 
            data = {
                "remote_ip": remote_ip, 
                "remote_id": remote_id,
                "remote_pw": remote_pw, 
                "remote_db_ip" : remote_db_ip, 
                "remote_db_id" : remote_db_id,
                "remote_db_pw" : remote_db_pw,
                "question_id" : question.id
            }

            # json을 문자열로 변경하여 외부인자로 같이 보내준다. 
            data_str = json.dumps(data)
        
            # 외부 스크립트 파일의 경로
            external_script_path = os.path.join(BASE_DIR, 'test.py')

            # subprocess.check_output : 주어진 명령을 실행하고, 그 결과를 가져온다. 
            # stderr=subprocess.STDOUT : 오류가 발생하면 표준 출력에 표시된다. 
            # text=True : check_output의 반환값이 텍스트로 해석되도록 지정한다. 
            result = subprocess.check_output(['python', external_script_path, data_str], stderr=subprocess.STDOUT, text=True)

            # 외부 스크립트에서 반환한 "취약" 또는 "양호" 문자열에 공백을 제거 후,
            result = result.strip()

            # 개발 모드에서 외부 파일에서 반환했는지 확인하기 위한 출력코드
            print("외부 파일에서 돌아옴")
            print(result)
            
            # 해당 검사결과 데이터가 있는지 확인하고, 
            checked_relation = CheckedRelation.objects.filter(resource=resource_info, question=question).first()
            
            # 해당하는 객체가 이미 있으면 외부 스크립트에서 반환한 문자열로 수정하고
            if checked_relation:
                checked_relation.result = result
                checked_relation.save()
            else:
                # 해당하는 객체가 없으면 새로 생성합니다.
                CheckedRelation.objects.create(
                    resource=resource_info,
                    question=question,
                    result=result,
                )
        # 원격정보를 검사완료로 바꾼다. 
        resource_info.inspection_status = '검사완료'
        resource_info.save()
        return redirect('service-ready')
    else:
        # 유저랑 관련된 원격, 상태정보의 id별로 데이터를 정리하는 과정
        serviceDataDic = {}
        # user : 로그인 유저 정보
        user = request.user

        resource_info_list = ResourceInfo.objects.filter(user=user).values(
            'id',
            'remote_id', 
            'remote_ip', 
            'remote_pw',
            'resource_ip', 
            'resource_id', 
            'resource_pw',
            'info_memo', 
            'update_date',
            'inspection_status',
        ).order_by('-update_date')

        # 로그인 유저와 관련있는 원격, 상태 정보의 pk(id), 연관 점검사항 pk(id 리스트)
        relatedQuesion_list= ResourceInfo.objects.filter(user=user).values('id','questionList__id')
        
        # serviceDataDic의 원격, 상태 정보의 pk를 key, 값을 해당 데이터로 저장한다. 
        # 관련 점검사항 id리스트를 'questionList__id' 키에 값으로 지정하기 위함이다. 
        for item in resource_info_list:
            serviceDataDic[item['id']] = item
            serviceDataDic[item['id']]['questionList__id'] = []

        for item in relatedQuesion_list:
            serviceDataDic[item['id']]['questionList__id'].append(item['questionList__id'])

        return render(request, 'service_ready.html', {'serviceDataList' : serviceDataDic.values()})

# 선택 서비스 및 결과 반환 
def service_result(request):
    service_result_data = {
        "LINUX" : [],
        "TOMCAT": [], 
        "NGINX" : [], 
        "MYSQL" : [], 
        "DOCKER": []
    }
    # 현재 로그인한 유저이면서 inspection_status가 검사완료인 ResourceInfo를 가져온다.
    current_user = request.user
    
    # 현재 로그인한 사용자와 관련된 검사 완료된 ResourceInfo 가져오기
    completed_resources = ResourceInfo.objects.filter(user=current_user, inspection_status='검사완료')

    for resource in completed_resources:
        for question in resource.questionList.all():
            to_append_dic = {}
            
            matching_question = SecurityQuestion.objects.get(id=question.id)
            to_append_dic['category'] = question.category
            to_append_dic['question'] = question.question
            to_append_dic['info_memo'] = resource.info_memo
            # ast.literal_eval() : 리스트 형태인 문자열을 리스트로 변경하기 위해 사용된다. 
            to_append_dic['action_taken'] =  ast.literal_eval(question.actionTaken)
            to_append_dic['result'] = question.actionTaken

            try:
                checked_relation = CheckedRelation.objects.get(resource=resource, question=matching_question)
                
                to_append_dic['result'] = checked_relation.result
                to_append_dic['date'] = checked_relation.date
            except CheckedRelation.DoesNotExist:
                print("No Checked Relation Found")
            service_result_data[matching_question.qType].append(to_append_dic)
    '''
    service_result_data의 예시) 
    {
        'LINUX': 
            [{  'category': '계정관리', 
                'question': 'root 계정 원격 접속 제한', 
                'info_memo': '내거 u01, u04', 
                'action_taken': [ "1. vi 편집기를 이용하여 /etc/ssh/sshd_config 파일을 연다. vi /etc/ssh/sshd_config 입력, ",
                                "2. PermitRootLogin 찾는다 /permitRootLogin를 치고 엔터를 누르면 찾을 수 있다."],
                'result': '취약', 
                'date': datetime.date(2024, 6, 10)}, 
            {   'category': '계정관리', 
                'question': '패스워드 최대 사 용 기간 설정', 
                'info_memo': '내거 u01, u04', 
                'action_taken': ["1. vi /etc/login.defs 입력", "2. PASS_MAX_DAYS 90 으로 수정하여 패스워드 설정기간을 90일 이내로 설정한다."]
                'result': '취약', 
                'date': datetime.date(2024, 6, 10)
            }],
        'TOMCAT': [],
        'NGINX': [], 
        'MYSQL': [], 
        'DOCKER': []
    }
    '''
    return render(request, 'service-result.html', {"service_result_data" : service_result_data})