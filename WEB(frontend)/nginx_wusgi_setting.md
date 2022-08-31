
다음과 같이 uwsgi 설정

경로 : `/etc/uwsgi/apps-enabled`

*주의 : pid 가 `/usr/share/uwsgi/conf/default.ini`  파일의 pid와 중복설정 되지 않도록 조심할 것!

```bash
# uwsgi.ini
[uwsgi]
base = /home/ubuntu/gk/WEB(frontend)
#server_dev:프로젝트 파일명

#가상환경 경로
home = /home/ubuntu/gk/WEB(frontend)/myenv
# 프로젝트 경로
chdir = /home/ubuntu/gk/WEB(frontend)
#프로젝트명.wsgi:application
module = wsgi:app
# app.py

#나중에 리눅스 소켓을 통한 통신 할 때 사용할 소켓 경로 - nginx 설정과 같게 해야함.
socket = /data/kurlycheck/tmp/kurlycheck.sock
#socket = /run/uwsgi/app/kurlycheck/kurlycheck.sock
chmod-socket = 666 

#master = true
enable-threads = true
#pidfile = /data/kurlycheck/tmp/flask.pid

plugin=python3

vaccum = true
#logger = /data/kurlycheck/log/uwsgi.log
```

nginx 설정

`/etc/nginx/sites-enabled/myflask`

```bash
server{
        listen 80;
        server_name (도메인);

        location / {
                include uwsgi_params;
                uwsgi_pass unix:/data/kurlycheck/tmp/kurlycheck.sock;
        }
}
```
