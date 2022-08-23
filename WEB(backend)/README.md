# Weight_Check Backend Server
Weight_Check 백엔드 서버입니다

## 실행
```shell
flask run
```

## 라이브러리 설치
```shell
cd "./WEB(backend)/venv/Scripts"
pip.exe install -r ../../requirements.txt
```

## 라이브러리 목록 저장
```shell
cd "./WEB(backend)/venv/Scripts"
pip.exe freeze > ../../requirements.txt
```

## DB 키 초기세팅
db의 링크와 아이디, 비밀번호가 노출되면 곤란하기에 환경변수로 키 값을 관리합니다
아래 중 하나만 해주시면 됩니다.

했는데 실행이 안된다! -> 파이참 껐다 키세요

### Window PowerShell
```shell
$env:KurlyCheckDbHost = "0.0.0.0"
$env:KurlyCheckDbPort = "7778"
$env:KurlyCheckDbUser = "admin"
$env:KurlyCheckDbPswd = "*******"
```

### Window CMD
```shell
setx KurlyCheckDbHost 0.0.0.0
setx KurlyCheckDbPort 7778
setx KurlyCheckDbUser admin
setx KurlyCheckDbPswd *******
```

### Bash/Ubunto
```shell
export KurlyCheckDbHost=0.0.0.0
export KurlyCheckDbPort=7778
export KurlyCheckDbUser=admin
export KurlyCheckDbPswd=*******
```
