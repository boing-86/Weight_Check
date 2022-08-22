$(document).ready(function () {
    showRealWeight();
});

function showRealWeight() { //실제 중량 보여 주기 GET
    $('c').empty() //<c> 요소 내용 지우기
    $.ajax({ //ajax 호출
        type: 'GET',
        url: '/api/main/real_weight',
        data: {},
        success: function (response) {
            let realWeight = response['']
            let html = `<div class="input-box">
                            <div class="inner-input">
                            <p></p>
                            <c>${}</c>
                            </div>`

        },
        error: function () {
            alert("중량을 가져올 수 없습니다.")
        }
    })
}

function showExpectationWeight() { //예상 중량 보여 주기 GET
    $('c').empty() //<c> 요소 내용 지우기
    $.ajax({
        type: 'GET',
        url: '/api/main/exp_weight',
        data: {},
        success: function (response) {
            let expWeight = response['']
        },
        error: function () {
            alert("중량을 가져올 수 없습니다.")
        }
    })
}

function showResult() { //결과 보여 주기 GET
    $('b').empty() //<b> 요소 내용 지우기
    $.ajax({
        type: 'GET',
        url: '/api/main/result',
        data: {},
        success: function (response) {
            let result = response['']
        },
        error: function () {
            alert("결과를 가져올 수 없습니다.")
        }
    })
}