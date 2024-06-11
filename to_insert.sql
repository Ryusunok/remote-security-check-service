INSERT INTO myapp_securityquestion (id, category, question, qType, actionTaken) VALUES (
    'U-01', '계정관리', 'root 계정 원격 접속 제한', 'LINUX', '["1. vi 편집기를 이용하여 /etc/ssh/sshd_config 파일을 연다. vi /etc/ssh/sshd_config 입력", 
"2. PermitRootLogin 찾는다 /permitRootLogin를 치고 엔터를 누르면 찾을 수 있다."]');


INSERT INTO myapp_securityquestion (id, category, question, qType, actionTaken) VALUES (
'U-04', '계정관리', '패스워드 최대 사용 기간 설정', 'LINUX', '["1. vi /etc/login.defs 입력", "2. PASS_MAX_DAYS 90 으로 수정하여 패스워드 설정기간을 90일 이내로 설정한다."]');

INSERT INTO myapp_securityquestion (id, category, question, qType, actionTaken) VALUES (
'U-05', '계정관리', '패스워드 파일 보호', 'LINUX', '["1. 쉐도우 패스워드 정책 적용을 위해 pwconv입력하거나", "2. 일반 패스워드 정책 적용을 위해 pwunconv를 입력한다."]');


INSERT INTO myapp_securityquestion (id, category, question, qType, actionTaken) VALUES (
'U-06', '파일 및 디렉토리 관리', 'root 홈, 패스 디렉터리 권한 및 패스 설정', 'LINUX', '["1. vi 편집기를 이용하여 root 계정의 설정파일을 연다. vi /etc/profile", "2. PATH=$PATH:HOME/bin 과 같이 수정한다."]');


INSERT INTO myapp_securityquestion (id, category, question, qType, actionTaken) VALUES (
'U-07', '파일 및 디렉토리 관리', 'root 홈, 패스 디렉터리 소유자 설정', 'LINUX', '["1. 소유자가 존재하지 않는 파일이나 디렉터리가 불필요한 경우 rm 명령으로 삭제한다.", "2. rm <file_name> 또는 rm -rf <directory_name>"]');

INSERT INTO myapp_securityquestion (id, category, question, qType, actionTaken) VALUES (
'U-08', '파일 및 디렉토리 관리', '/etc/passwd 파일 소유자 및 권한 설정', 'LINUX', '["1. /etc/passwd 파일의 소유자 및 권한 변경(소유자 root, 권한 644).", "2. chown root /etc/passwd 그리고 chmod 644 /etc/passwd"]');

INSERT INTO myapp_securityquestion (id, category, question, qType, actionTaken) VALUES (
'U-09', '파일 및 디렉토리 관리', '/etc/shadow 파일 소유자 및 권한 설정', 'LINUX', '["1. /etc/shadow 파일의 소유자 및 권한 변경(소유자 root, 권한 400).", "2. chown root /etc/shadow 그리고 chmod 400 /etc/shadow"]');

INSERT INTO myapp_securityquestion (id, category, question, qType, actionTaken) VALUES (
'U-10', '파일 및 디렉토리 관리', '/etc/hosts 파일 소유자 및 권한 설정', 'LINUX', '["1. /etc/hosts 파일의 소유자 및 권한 변경(소유자 root, 권한 644).", "2. chown root /etc/hosts 그리고 chmod 644 /etc/hosts"]');

INSERT INTO myapp_securityquestion (id, category, question, qType, actionTaken) VALUES (
'U-13', '파일 및 디렉토리 관리', '/etc/services 파일 소유자 및 권한 설정', 'LINUX', '["1. /etc/services  파일의 소유자 및 권한 변경(소유자 root, 권한 644).", "2. chown root /etc/services  그리고 chmod 644 /etc/services"]');

