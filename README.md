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
  
## 사용
- docker(컨테이너), mariadb(db), django(웹)
 
