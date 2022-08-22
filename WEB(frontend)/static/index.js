$(document).ready(function () {
    UpdateProductInfo();
});

var g_weight = 0, g_barcode = 0;
var exp_weight_min, exp_weight_max;

function UpdateWidgets() {
    if (!!g_weight)
        $('#real_weight').innerText = `${g_weight} kg`;
    else
        $('#real_weight').innerText = `측정 중`;

    if (!!g_weight && !!g_barcode) { // exp_weight 값 있을 때
        if (g_weight < exp_weight_min)
            $('#result_box').innerText = `${g_weight-exp_weight_min} kg이 부족합니다.`;
        else if (g_weight > exp_weight_max)
            $('#result_box').innerText = `${exp_weight_max-g_weight} kg이 초과입니다.`;
        else {
            $('#result_box').innerText = 'PASS';
            //색깔 변경 해야 함
        }
    }
    else {
        $('#result_box').innerText = "";
    }

}

function UpdateProductInfo() { // 실제 중량 가져 오기
    $.ajax({
        type: 'POST',
        url: 'https://localhost:5000/real_weight',
        data: {},
        success(response) {
            g_weight = response['weight'];
            g_barcode = response['barcode'];

            if (!!g_weight && !!g_barcode)
                UpdateExpectedWeight();
            UpdateWidgets();
        },
        error() {
            alert('중량을 가져올 수 없습니다.');
        }
    });
}

function UpdateExpectedWeight() { //예상 중량 보여 주기 GET
    $.ajax({
        type: 'GET',
        url: '/api/main/exp_weight',
        data: {},
        success(response) {
            exp_weight_min = response['min']
            exp_weight_max = response['max']

            $('#exp_weight').innerText = `${exp_weight_min} kg ~ ${exp_weight_max} kg`;
        },
        error() {
            alert('중량을 가져올 수 없습니다.')
        }
    })
}

function PostProductInfo() { //결과 보여 주기 GET
    $('b').empty() //<b> 요소 내용 지우기
    $.ajax({
        type: 'GET',
        url: '/api/main/result',
        data: {},
        success(response) {
            let result = response['']
        },
        error() {
            alert('결과를 가져올 수 없습니다.')
        }
    })
}