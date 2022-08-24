# Weight_Check Frontend Server
프론트엔드 서버입니다.

웹 파일을 반환하는 웹 서버 입니다.

### 라이브러리 설치
```shell
cd "./WEB(frontend)/venv/Scripts"
pip.exe install -r ../../requirements.txt
```

### 라이브러리 목록 저장
```shell
cd "./WEB(frontend)/venv/Scripts"
pip.exe freeze > ../../requirements.txt
```

## Backend Server 연결 설정
Backend Server의 Host와 Port가 노출되면 곤란하기에 환경변수로 키 값을 관리합니다
아래 중 하나만 해주시면 됩니다.

했는데 실행이 안된다! -> 파이참 재실행하시면 됩니다.

### Window PowerShell
```shell
$env:KurlyCheckBeHost = "0.0.0.0"
$env:KurlyCheckBePort = "7778"
```

### Window CMD
```shell
setx KurlyCheckBeHost 0.0.0.0
setx KurlyCheckBePort 7778
```

### Bash/Ubuntu
```shell
export KurlyCheckBeHost=0.0.0.0
export KurlyCheckBePort=7778
```
