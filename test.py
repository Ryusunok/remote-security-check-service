import sys
import os
import paramiko
import json

def ssh_remote_command(host, username, password, question_id):
    # SSH 클라이언트 생성
    client = paramiko.SSHClient()

    # 호스트 키 자동으로 확인 (보안상의 이유로 추천되지 않음)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = ""
    try:
        # SSH 연결
        client.connect(hostname=host, username=username, password=password)

        # 아래의 if-elif 조건문은 question_id에 따라 달라진다. 
        # question_id에 따라 "취약" 또는 "양호" 조건이 달라진다. 
        # 이것을 if-elif 조건문으로 표현하는 것이 아니라 점검사항DB에 해당 정보가 저장된 컬럼을 추가하여 db에 조건식을 저장하려고 하였으나,  
        # eval()을 활용하여도 에러가 발생했음 -> 추후 더 효율적인 코드로 변경할 필요가 있음
        if question_id == 'U-01':
            stdin, stdout, stderr = client.exec_command('grep "^PermitRootLogin" /etc/ssh/sshd_config')
            permit_root_login = stdout.read().decode().strip()

            if "PermitRootLogin no" in permit_root_login:
                result = "양호"
            else:
                result = "취약"
            client.close()

        elif question_id == 'U-04':
            stdin, stdout, stderr = client.exec_command('grep "^PASS_MAX_DAYS" /etc/login.defs')
            pass_max_days = stdout.read().decode().strip()

            if "PASS_MAX_DAYS" in pass_max_days and int(pass_max_days.split()[1]) <= 90:
                result = "양호"
            else:
                result = "취약"
            client.close()

        elif question_id == 'U-05':
            stdin, stdout, stderr = client.exec_command('ls -l /etc/shadow')
            shadow_details = stdout.read().decode().strip()

            if shadow_details:
                result = "양호"
            else:
                stdin, stdout, stderr = client.exec_command('cat /etc/passwd')
                passwd_content = stdout.read().decode().strip()
                passwd_lines = passwd_content.split('\n')

                all_x = True
                for line in passwd_lines:
                    fields = line.split(':')
                    if len(fields) > 1 and fields[1] != 'x':
                        all_x = False
                        break
                if all_x:
                    result = "양호"
                else:
                    result = "취약"
            client.close()

        elif question_id == 'U-06':
            stdin, stdout, stderr = client.exec_command('echo $PATH')
            path_variable = stdout.read().decode().strip()
            
            path_elements = path_variable.split(':')
            if '.' in path_elements and (path_elements[0] == '.' or '.' in path_elements[1:]):
                result = "취약"
            else:
                result = "양호"
            client.close()
        
        elif question_id == 'U-07':
            stdin, stdout, stderr = client.exec_command('find / -nouser -o -nogroup')
            find_results = stdout.read().decode().strip()

            if find_results:
                result = "취약"
            else:
                result = "양호"
            client.close()

        elif question_id == 'U-08':
            stdin, stdout, stderr = client.exec_command('ls -l /etc/passwd')
            passwd_details = stdout.read().decode().strip()

            parts = passwd_details.split()
            permissions = parts[0]
            owner = parts[2]

            if owner == 'root':
                if permissions[1:4] == 'rw-' and (permissions[4:7] == 'r--') and (permissions[7:10] == 'r--' or permissions[7:10] == '---'):
                    result = "양호"
                else:
                    result = "취약"
            else:
                result = "취약"
            client.close()
        
        elif question_id == 'U-09':
            stdin, stdout, stderr = client.exec_command('ls -l /etc/shadow')
            shadow_details = stdout.read().decode().strip()

            parts = shadow_details.split()
            permissions = parts[0]
            owner = parts[2]

            if owner == 'root':
                if permissions[1:4] == 'r--' and permissions[4:7] == '---' and permissions[7:10] == '---':
                    result = "양호"
                else:
                    result = "취약"
            else:
                result = "취약"
            client.close()
        
        elif question_id == 'U-10':
            stdin, stdout, stderr = client.exec_command('ls -l /etc/hosts')
            hosts_details = stdout.read().decode().strip()

            parts = hosts_details.split()
            permissions = parts[0]
            owner = parts[2]

            if owner == 'root':
                if permissions[1:4] == 'rw-' and permissions[4:7] == 'r--' and (permissions[7:10] == 'r--' or permissions[7:10] == '---'):
                    result = "양호"
                else:
                    result = "취약"
            else:
                result = "취약"
            client.close()
        
        elif question_id == 'U-13':
            stdin, stdout, stderr = client.exec_command('ls -l /etc/services')
            services_details = stdout.read().decode().strip()

            parts = services_details.split()
            permissions = parts[0]
            owner = parts[2]

            if owner == 'root':
                if permissions[1:4] == 'rw-' and permissions[4:7] == 'r--' and (permissions[7:10] == 'r--' or permissions[7:10] == '---'):
                    result = "양호"
                else:
                    result = "취약"
            else:
                result = "취약"
            client.close()

        elif question_id == 'U-19':
            stdin, stdout, stderr = client.exec_command('ls -l /etc/cron.allow')
            cron_allow_details = stdout.read().decode().strip()

            parts = cron_allow_details.split()
            permissions = parts[0]
            owner = parts[2]

            if owner == 'root':
                if permissions[1:4] == 'rw-' and (permissions[4:7] == 'r--' or permissions[4:7] == '---') and permissions[7:10] == '---':
                    result = "양호"
                else:
                    result = "취약"
            else:
                result = "취약"
            client.close()
        return result
    except Exception as e:
        return str(e)

# 원격 SSH 접속 정보
'''
data의 타입 : dictionary 
ex) data = {
        'remote_ip': '100.100.100.73', 
        'remote_id': 'user', 
        'remote_pw': 'user', 
        'remote_db_ip': '', 
        'remote_db_id': '', 
        'remote_db_pw': '',
        'question_id': 'U-04'
    }
'''
# sys.argv[1] : views.py에서 해당 파이썬 코드를 실행할 때, 같이 보내준 인자
# views.py에서 인자로 보낼 때, json 형태의 문자열로 보냈기 때문에 
# 이것을 다시 json형태로 변환하기 위해 json.loads()를 사용한다.
data = json.loads(sys.argv[1])

host = data['remote_ip']
username = data['remote_id']
password = data['remote_pw']
question_id = data['question_id']

# SSH로 명령 실행
# 점검사항의 pk, 즉, question_id에 따라 "양호" 또는 "취약"인지 판단하는 조건문이 달라지기 때문에
# 필수적으로 question_id가 필요하다. 
# ssh로 원격 접속할 때, remote_ip, remote_id, remote_pw가 당연히 필수적으로 필요하다
result = ssh_remote_command(host, username, password, question_id)

# 여기서 print로 출력하면 이 파이썬 코드를 실행한 views.py에서 사용할 수 있다.
print(result)
