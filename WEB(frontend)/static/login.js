user_id = $("#username-field").val()
user_pw = $("#password-field").val()
warning = $("#form-warning")

if (!user_id && !user_pw)
    warning.text('');
else if (!user_id.match(/^[A-Za-z]+[A-Za-z0-9]{5,19}$/g))
    warning.text("아이디가 일치하지 않습니다.");
else if (!user_pw.match(/^(?=.*[a-zA-z])(?=.*[0-9])(?=.*[$`~!@$!%*#^?&\\(\\)\-_=+]).{8,16}$/))
    warning.text("비밀번호는 영문, 숫자, 특수문자 조합으로 8~16글자 입니다.");
else
    warning.text("아이디 또는 비밀번호가 일치하지 않습니다.");