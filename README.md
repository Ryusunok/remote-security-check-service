## remote-security-check-service
원격 보안 점검 서비스

- docker compose up -d 명령어 실행 시, was, db 컨테이너가 실행된다.

- docker exec -it was /bin/bash
- python manage.py makemigrations myapp
- python manage.py migrate myapp
- python manage.py migrate sessions
-> 장고의 models.py에 따라 테이블이 생성된다.

## 추후 보안 예정
- 보안 점검사항의 항목을 늘린다.
- aws에 프로그램을 올려서 실제로 사용할 수 있는 서비스를 제공한다.
- 발표 -> 코드 내용 안보임 -> 무엇을 하는 기능인지
-- 검사 시작 시, 로그 찍어주거나, 몇개중에 몇개가 진행중인지 띄우기  
-- 보안 결과를 양호, 취약이 아니라 중요도(상, 중, 하)에 따라서 몇점 이상 판단해서 전체적인 스코어를 매겼으면 좋았겠다. 

## 사용
- docker(컨테이너), mariadb(db), django(웹)
 
