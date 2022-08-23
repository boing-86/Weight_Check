$(document).ready(function () {
    UpdateWeight();
    UpdateProductInfo();
});

let g_weight = 0, g_barcode = 0;
let exp_weight_min, exp_weight_max;

let $weight = $('#real_weight');
let $result_box = $('#result_box');

function UpdateProductInfo() { // 실제 중량 가져 오기
    $.ajax({
        type: 'GET',
        url: 'http://localhost:5000/real_weight',
        dataType: 'jsonp',
        jsonpCallback: "getInfo",
        success(response) {
            g_weight = response['weight'];
            g_barcode = response['barcode'];

            UpdateWeight();
            UpdateResult();
            // if (!!g_weight && !!g_barcode)
            //     UpdateExpectedWeight();

            sleep(300)
            UpdateProductInfo();
        },
        error() {
            alert('You cannot bring the real weight.');
        }
    });
}

function UpdateExpectedWeight() { //예상 중량 보여 주기 GET
    $.ajax({
        type: 'POST',
        url: '/api/main/exp_weight',
        data: {"id": g_barcode},
        success(response) {
            exp_weight_min = response['min'];
            exp_weight_max = response['max'];

            UpdateExpWeight();
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

function UpdateWeight() {
    $weight.text(`${g_weight} kg`);
}

function UpdateExpWeight() {
    $('#exp_weight').text(`${exp_weight_min} kg ~ ${exp_weight_max} kg`);
}

function UpdateResult() {
    $result_box.css('color', 'red');
    $result_box.css('font-size', '3rem');

    if (!g_barcode)
        $result_box.text('');
    else if (g_weight < exp_weight_min)
        $result_box.text(`${exp_weight_max - g_weight} kg이 부족합니다.`);
    else if (g_weight > exp_weight_max)
        $result_box.text(`${g_weight - exp_weight_max} kg이 초과합니다.`);
    else {
        $result_box.text('PASS');
        $result_box.css('color', 'green');
        $result_box.css('font-size', '9rem');
    }
}

function sleep(t) {
    let time = Date.now() + t
    while (Date.now() <= time) {}
}