import json
import os
from flask import Flask, request
import base64

app = Flask(__name__)

class Config:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """설정을 로드합니다. 우선순위: 환경변수 > config.json > 기본값"""
        
        # 기본 설정값
        defaults = {
            'username': 'root',
            'password': 'your_password_here',
            'ssh_key': 'your_ssh_key_here',
            'server_host': '0.0.0.0',
            'server_port': 8080,
            'storage_layout': 'direct'
        }
        
        # config.json 파일에서 로드 시도
        config_data = {}
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                    config_data = {
                        'username': json_config.get('default_user', {}).get('username', defaults['username']),
                        'password': json_config.get('default_user', {}).get('password', defaults['password']),
                        'ssh_key': json_config.get('ssh', {}).get('public_key', defaults['ssh_key']),
                        'server_host': json_config.get('server', {}).get('host', defaults['server_host']),
                        'server_port': json_config.get('server', {}).get('port', defaults['server_port']),
                        'storage_layout': json_config.get('storage', {}).get('layout_name', defaults['storage_layout'])
                    }
                print(f"✅ Config loaded from {config_file}")
            except Exception as e:
                print(f"⚠️  config.json 로드 실패: {e}")
                config_data = defaults
        else:
            print("⚠️  config.json 파일이 없습니다. 환경변수 또는 기본값을 사용합니다.")
            config_data = defaults
        
        # 환경변수로 오버라이드 (우선순위 높음)
        self.username = os.getenv('DEFAULT_USERNAME', config_data['username'])
        self.password = os.getenv('DEFAULT_PASSWORD', config_data['password'])
        self.ssh_key = os.getenv('SSH_PUBLIC_KEY', config_data['ssh_key'])
        self.server_host = os.getenv('SERVER_HOST', config_data['server_host'])
        self.server_port = int(os.getenv('SERVER_PORT', config_data['server_port']))
        self.storage_layout = os.getenv('STORAGE_LAYOUT', config_data['storage_layout'])
        
        # 환경변수가 사용되었는지 확인
        env_vars_used = []
        if os.getenv('DEFAULT_USERNAME'): env_vars_used.append('DEFAULT_USERNAME')
        if os.getenv('DEFAULT_PASSWORD'): env_vars_used.append('DEFAULT_PASSWORD')
        if os.getenv('SSH_PUBLIC_KEY'): env_vars_used.append('SSH_PUBLIC_KEY')
        if os.getenv('SERVER_HOST'): env_vars_used.append('SERVER_HOST')
        if os.getenv('SERVER_PORT'): env_vars_used.append('SERVER_PORT')
        if os.getenv('STORAGE_LAYOUT'): env_vars_used.append('STORAGE_LAYOUT')
        
        if env_vars_used:
            print(f"✅ 환경변수로 오버라이드된 설정: {', '.join(env_vars_used)}")
        
        # 보안 경고
        if self.password in ['your_password_here', 'dlsvmfk00##']:
            print("🚨 경고: 기본 비밀번호를 사용 중입니다. config.json 또는 환경변수로 변경하세요!")
        
        if self.ssh_key == 'your_ssh_key_here':
            print("🚨 경고: 기본 SSH 키를 사용 중입니다. config.json 또는 환경변수로 변경하세요!")

# 전역 설정 인스턴스
config = Config()

@app.route("/vm/<vmname>/user-data")
def user_data(vmname):
    """VM별 cloud-init user-data 생성"""
    
    user_data = f"""#cloud-config
growpart:
  mode: 'off'
locale: en_US.UTF-8
preserve_hostname: true
resize_rootfs: false
ssh_pwauth: true

users:
  - name: deploy
    gecos: {vmname}
    groups: adm,cdrom,dip,lxd,plugdev,sudo
    lock_passwd: false
    plain_text_passwd: {config.password}
    shell: /bin/bash
    ssh_authorized_keys:
      - {config.ssh_key}
"""
    # base64 encode
    cloud_config_b64 = base64.b64encode(user_data.encode("utf-8")).decode("utf-8")
    return cloud_config_b64, 200, {'Content-Type': 'text/plain'}

@app.route("/vm/<vmname>/meta-data")
def meta_data(vmname):
    """VM별 cloud-init meta-data 생성"""
    meta_data = f"""instance-id: {vmname}
local-hostname: {vmname}
"""
    return meta_data, 200, {'Content-Type': 'text/plain'}

@app.route("/health")
def health():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "config_source": "config.json + environment variables"
    }

@app.route("/config/status")
def config_status():
    """현재 설정 상태 확인 (민감정보 제외)"""
    return {
        "username": config.username,
        "password_configured": "Yes" if config.password != 'your_password_here' else "No (using default)",
        "ssh_key_configured": "Yes" if config.ssh_key != 'your_ssh_key_here' else "No (using default)",
        "server_host": config.server_host,
        "server_port": config.server_port,
        "storage_layout": config.storage_layout
    }

if __name__ == "__main__":
    print("🚀 Ubuntu AutoInstall Server 시작")
    print(f"📡 서버 주소: http://{config.server_host}:{config.server_port}")
    print(f"👤 기본 사용자: {config.username}")
    print(f"💾 스토리지 레이아웃: {config.storage_layout}")
    print("\n📋 사용 가능한 엔드포인트:")
    print(f"  - http://{config.server_host}:{config.server_port}/vm/<vmname>/user-data")
    print(f"  - http://{config.server_host}:{config.server_port}/vm/<vmname>/meta-data")
    print(f"  - http://{config.server_host}:{config.server_port}/health")
    print(f"  - http://{config.server_host}:{config.server_port}/config/status")
    print()
    
    app.run(host=config.server_host, port=config.server_port, debug=False)
