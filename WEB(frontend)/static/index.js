$(document).ready(function () {
    UpdateProductInfo();
});

let g_weight = 0, g_barcode = 0;
let exp_weight_min, exp_weight_max;

function UpdateWidgets() {
    if (!!g_weight)
        $('#real_weight').innerText = `${g_weight} kg`;
    else
        $('#real_weight').innerText = `측정 중`;

    if (!!g_weight && !!g_barcode) { // exp_weight 값 존재할 때
        $('#exp_weight').innerText = `${exp_weight_min} kg ~ ${exp_weight_max} kg`;

        if (g_weight < exp_weight_min)
            $('#result_box').innerText = `${g_weight-exp_weight_min} kg이 부족합니다.`;
        else if (g_weight > exp_weight_max)
            $('#result_box').innerText = `${exp_weight_max-g_weight} kg이 초과합니다.`;
        else {
            $('#result_box').innerText = 'PASS';
            $('#result_box').css('color', 'green');
        }
        $('#result_box').css('color', 'red');
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
            alert('실제 중량을 가져올 수 없습니다.');
        }
    });
}

function UpdateExpectedWeight() { //예상 중량 보여 주기 GET
    $.ajax({
        type: 'POST',
        url: '/api/main/exp_weight',
        data: {"id": g_barcode},
        success(response) {
            exp_weight_min = response['min']
            exp_weight_max = response['max']

            PostProductInfo();
        },
        error() {
            alert('예측 중량을 가져올 수 없습니다.')
        }
    })
}

function PostProductInfo() { //결과 보내 주기 GET
    $.ajax({
        type: 'POST',
        url: '/api/main/result',
        data: {"id": g_barcode, "weight": g_weight},
        success(response) {},
        error() {
            alert('결과를 보낼 수 없습니다.')
        }
    })
}