# Ubuntu AutoInstall Server

Ubuntu 자동 설치를 위한 cloud-init 서버입니다. 민감한 정보는 별도 설정 파일로 관리합니다.

## 🔧 설정 방법

### 방법 1: JSON 설정 파일 (권장)

1. `config.json` 파일 생성:
```bash
cp config.json.example config.json  # 예시가 있다면
# 또는 직접 생성
```

2. `config.json` 내용을 실제 값으로 수정:
```json
{
  "default_user": {
    "username": "your_username",
    "password_hash": "your_actual_password_hash"
  },
  "ssh": {
    "public_key": "your_actual_ssh_public_key"
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8080
  },
  "storage": {
    "layout_name": "direct"
  }
}
```

### 방법 2: 환경 변수

1. 환경 변수 설정:
```bash
# .env 파일 생성
cp config.env.example .env

# 실제 값으로 수정
vim .env
```

2. 환경 변수 로드:
```bash
# .env 파일 로드
export $(cat .env | xargs)

# 또는 직접 설정
export DEFAULT_USERNAME="your_username"
export DEFAULT_PASSWORD_HASH="your_password_hash"
export SSH_PUBLIC_KEY="your_ssh_public_key"
```

## 🚀 서버 실행

### 가상환경 설정 (권장)
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# Flask 설치
pip install flask

# 서버 실행
python server.py
```

### 직접 실행
```bash
# Flask 설치 (시스템 전역)
pip3 install --user flask

# 서버 실행
python3 server.py
```

## 📋 API 엔드포인트

| 엔드포인트 | 설명 | 예시 |
|-----------|------|------|
| `/vm/<vmname>/user-data` | cloud-init user-data | `/vm/test-vm/user-data` |
| `/vm/<vmname>/meta-data` | cloud-init meta-data | `/vm/test-vm/meta-data` |
| `/health` | 서버 상태 확인 | `/health` |
| `/config/status` | 설정 상태 확인 | `/config/status` |

## 🔐 보안 주의사항

1. **민감 정보 분리**: `config.json`과 `.env` 파일은 버전 관리에서 제외됩니다.

2. **비밀번호 해시**: 평문 비밀번호가 아닌 해시된 비밀번호를 사용하세요:
```bash
# Ubuntu에서 비밀번호 해시 생성
python3 -c "import crypt; print(crypt.crypt('your_password', crypt.mksalt(crypt.METHOD_SHA512)))"
```

3. **SSH 키 생성**:
```bash
# SSH 키 쌍 생성
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 공개키 복사
cat ~/.ssh/id_rsa.pub
```

## 🛠️ ESXi에서 사용하기

1. **ISO 부팅 시 kernel 파라미터에 추가**:
```
autoinstall ds=nocloud-net;s=http://YOUR_SERVER_IP:8080/vm/VM_NAME/
```

2. **예시**:
```
autoinstall ds=nocloud-net;s=http://192.168.1.100:8080/vm/test-ubuntu/
```

## 📁 파일 구조

```
autoinstall/
├── server.py              # 메인 서버 파일
├── config.json            # JSON 설정 파일 (생성 필요)
├── config.env.example     # 환경변수 예시
├── .env                   # 환경변수 파일 (생성 필요)
├── .gitignore            # 버전 관리 제외 목록
└── README.md             # 이 파일
```

## 🔄 설정 우선순위

1. **환경 변수** (최우선)
2. **config.json 파일**
3. **기본값** (개발용)

## 🎯 사용 예시

### 1. 서버 시작
```bash
$ python3 server.py
🚀 Ubuntu AutoInstall Server 시작
✅ Config loaded from /path/to/config.json
📡 서버 주소: http://0.0.0.0:8080
👤 기본 사용자: ubuntu
💾 스토리지 레이아웃: direct

📋 사용 가능한 엔드포인트:
  - http://0.0.0.0:8080/vm/<vmname>/user-data
  - http://0.0.0.0:8080/vm/<vmname>/meta-data
  - http://0.0.0.0:8080/health
  - http://0.0.0.0:8080/config/status
```

### 2. 설정 상태 확인
```bash
curl http://localhost:8080/config/status
```

## 🔧 문제해결

### 설정 파일이 로드되지 않을 때
```bash
# 파일 경로 확인
ls -la config.json

# 권한 확인
chmod 600 config.json

# JSON 문법 확인
python3 -m json.tool config.json
```

### Flask가 설치되지 않을 때
```bash
# 가상환경 사용 (권장)
python3 -m venv venv
source venv/bin/activate
pip install flask

# 또는 사용자 디렉토리에 설치
pip3 install --user flask
``` 
