$(document).ready(function () {
    UpdateWidgets();
    UpdateProductInfo();
    // UpdateProductInfoJsonp();
});

let g_weight = 0, g_barcode = 0;
let exp_weight_min, exp_weight_max;

// 기존 정보를 바탕으로 UI를 한번에 업데이트 합니다.
function UpdateWidgets() {
    if (!!g_weight)
        $('#real_weight').text(`${g_weight} kg`);
    else
        $('#real_weight').text(`측정 중`);

    if (typeof exp_weight_max === 'number') { // exp_weight 값 존재할 때
        $('#exp_weight').text(`${exp_weight_min} kg ~ ${exp_weight_max} kg`);

        let _result_box = $('#result_box');
        if (g_weight < exp_weight_min)
            _result_box.text(`${g_weight - exp_weight_min} kg이 부족합니다.`);
        else if (g_weight > exp_weight_max)
            _result_box.text(`${exp_weight_max - g_weight} kg이 초과합니다.`);
        else {
            _result_box.text('PASS');
            _result_box.css('color', 'green');
        }
        _result_box.css('color', 'red');
    }
    else {
        $('#result_box').text('');
        $('#exp_weight').text('바코드를 찍어주세요')
    }
}

function UpdateProductInfo() {
    $.ajax({
        type: 'GET',
        url: 'http://localhost:5000/real_weight',
        data: {},
        success(response) {
            g_barcode = response['barcode'];
            g_weight = response['weight'];

            // if (!!g_barcode)
            //     UpdateExpectedWeight();
            UpdateWidgets();
        },
        error() {
            alert('You cannot bring the real weight.');
        }
    });
}

function UpdateProductInfoJsonp() { // 실제 중량 가져 오기
    $.ajax({
        type: 'GET',
        url: 'http://localhost:5000/real_weight2',
        dataType: 'jsonp',
        jsonpCallback: "getInfo",
        success: (response) => {
            g_weight = response['weight'];
            g_barcode = response['barcode'];

            // if (!!g_weight && !!g_barcode)
            //     UpdateExpectedWeight();
            UpdateWidgets();
        },
        error: function(xhr, status, error) {
            console.log(xhr);
            console.log(status);
            console.log(error);
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
            alert('You cannot bring the exp weight.')
        }
    });
}

function PostProductInfo() { //결과 보내 주기 GET
    $.ajax({
        type: 'POST',
        url: '/api/main/result',
        data: {"id": g_barcode, "weight": g_weight},
        success(response) {},
        error() {
            alert('You cannot send info.')
        }
    });
}