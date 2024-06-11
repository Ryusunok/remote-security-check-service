from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

# 점검사항DB
class SecurityQuestion(models.Model):
    # pk 
    id = models.CharField(max_length = 10, primary_key = True)
    # 카테고리 ex) 계정관리
    category = models.CharField(max_length = 20)
    # 점검사항 내용 ex) root 계정 원격 접속 제한
    question = models.TextField()
    # 점검사항 항목 ex) LINUX, TOMCAT, NGINX, DOCKER, MYSQL
    qType = models.CharField(max_length = 50)
    # 조치사항 - 문자열 형태의 리스트 ex) '["1. vi /etc/login.defs 입력", "2. PASS_MAX_DAYS 90 으로 수정하여 패스워드 설정기간을 90일 이내로 설정한다."]'
    actionTaken = models.TextField()
   
    def __str__(self):
        return self.question

# 유저정보DB
class CustomUser(AbstractUser):
    # AbstractUser에서 기본적으로 제공하는 컬럼 중 username, password를 사용
    # 유저 전화번호 ex) 010-1111-2222
    user_tel = models.CharField(max_length = 15)
    # 유저 이메일 ex) abcd@gmail.com
    user_email = models.EmailField()
   
    def __str__(self):
        return self.username
        
# 유저가 기입한 원격접속시 필요한 데이터
# 연결된 점검사항과 유저정보, 검사 전후 상태정보도 포함하고 있다.
# 원격정보 및 상태정보DB
class ResourceInfo(models.Model):
    # 장고에서 class에 id를 직접 기입하지 않으면 자동으로 id(pk)를 생성해준다. 
    
    # ssh 원격 접속 시, 사용될 remote_ip, remote_id, remote_pw
    remote_id = models.CharField(max_length = 100)
    remote_ip = models.CharField(max_length = 100)
    remote_pw = models.CharField(max_length = 100)

    # mysql 등 db에 원격으로 접속하기 위해 추가적으로 필요한 정보 resource_ip, resource_id, resource_pw
    # mysql을 제외한 linux, nginx, tomcat, docker는 resource_ip, resource_id, resource_pw가 불필요하기 때문에
    # null= True를 통해 null값도 허용하고 있다. 
    resource_ip = models.CharField(max_length = 100, null= True)
    resource_id = models.CharField(max_length = 100, null= True)
    resource_pw = models.CharField(max_length = 100, null= True)

    # 사용자가 서비스를 등록할 때, 기억하기 쉽도록 메모를 입력할 수 있도록 한다. 
    # ex) "(주) 가나다 회사 개발 1팀 서버"
    info_memo = models.TextField(default=datetime.now())

    # 수정일자 
    update_date = models.DateField(auto_now=True)

    # 서비스의 상태 ex) '검사전' 또는 '검사완료'
    # 해당 값이 '검사전'일 때, 검사 시작 버튼이 활성화되어 보안 점검을 할 수 있다. 
    inspection_status = models.CharField(max_length=20, default='검사전')

    # 유저 : 원격정보 및 상태정보 = 일 대 다관계이다. 
    # 즉, 유저는 여러 원격, 상태정보를 기입하여 여러 서버에 보안 점검 서비스를 제공받을 수 있다. 
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    # 원격정보 및 상태정보 : 점검사항 = 다 대 다 관계이다.
    # 즉, 원격, 상태 정보에 여러 점검사항 항목이 해당될 수 있다. 
    # 반대로, 하나의 점검사항 항목은 여러 원격, 상태정보에 검사될 수 있다. 
    questionList = models.ManyToManyField(SecurityQuestion)

# 검사결과DB 
# 원격정보 및 상태정보 와 점검사항이 엮여질 때, 추가로 기입될 정보를 저장하는 테이블이다. 
# *추가로 기입될 정보 = 어떤 원격-상태정보인지, 어떤 점검사항인지, 검사 결과가 양호/취약, 검사일자) 
class CheckedRelation(models.Model):
    resource = models.ForeignKey(ResourceInfo, on_delete=models.CASCADE)
    question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    result = models.CharField(max_length = 300)
    date = models.DateField(auto_now_add = True)
