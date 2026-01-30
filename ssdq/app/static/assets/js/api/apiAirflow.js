const resultTranslate = {
    success: "Выполнен",
    queued: "В очереди",
    running: "Выполняется",
    failed: "Ошибка выполнения"
};


const statusTranslate = {
    enabled: "Активен",
    disabled: "Отключен"
};


const apiCall = (endpoint, controlId) => {
    const successMessageMap = {
        triggerDag: 'DAG добавлен в очередь',
        killDag: 'DAG успешно остановлен',
        pauseDag: 'Dag успешно выключен',
        unpauseDag: 'Dag успешно включен'
    };
    let response = true;

    // var controlId = $('#controlId').val() ? $('#controlId').val() : window.controlId;

    if (controlId && controlId != 0) {
        $.ajax({
            type: "POST",
            url: `/api/dags/${endpoint}?id=${controlId}`,
            headers: {"X-CSRFToken": csrf_token},
            dataType: "json",
            async: false,
            encode: true,
        }).done(function (data) {
            if (data === undefined) {
                Swal.fire({
                    icon: 'success',
                    title: successMessageMap[endpoint],
                    position: 'top-end',
                    showConfirmButton: false,
                    toast: true,
                    timer: 5000
                });
            } else {
                let result = resultTranslate[data.result];
                let status = statusTranslate[data.status];
                Swal.fire({
                    icon: 'info',
                    title: 'Статус: ' + status,
                    html: `Последний результат: ${result ? result : data.result} <br>Старт: ${data.startDate} <br>Окончание: ${data.endDate}`,
                    position: 'top-end',
                    showConfirmButton: true,
                    toast: true,
                    timer: 10000
                });
            };
        }).fail(function (data) {
            response = false;
            Swal.fire({
                icon: 'error',
                title: data.statusText,
                position: 'top-end',
                showConfirmButton: false,
                toast: true,
                timer: 5000
            });
        });
    } else {
        Swal.fire({
            icon: 'error',
            title: "Не выбран контроль",
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 5000
        });
    };
    return response;
};

$('#triggerDag, #killDag, #pauseDag, #unpauseDag, #statusDag')
    .on('click', function () {
        var controlId = $('#controlId').val() ? $('#controlId').val() : window.controlId;
        apiCall($(this).attr('id'), controlId);
    });

$('#dagToggle').on('click', function () {
    const $el = $(this);
    const active = $el.toggleClass('active').hasClass('active');

    $el
        .toggleClass('fa-toggle-on', active)
        .toggleClass('fa-toggle-off', !active);

    var controlId = $('#controlId').val() ? $('#controlId').val() : window.controlId;
    // Включить
    if (active) {
        apiCall('unpauseDag', controlId);
    } else {
        // Выключить
        apiCall('pauseDag', controlId);
    }
});

// Проверка статуса DAG. 
// Изменение состояния dagToggle в соответствии с полученным статусом.   
const getDagStatus = (controlId) => {
    $.ajax({
        type: "POST",
        url: `/api/dags/statusDag?id=${controlId}`,
        headers: {"X-CSRFToken": csrf_token},
        dataType: "json",
        encode: true,
    }).done(function (data) {
        const $toggle = $('#dagToggle');
        const enabled = data.status === 'enabled';

        $toggle
            .toggleClass('fa-toggle-on', enabled)
            .toggleClass('fa-toggle-off', !enabled);
    }).fail(function (data) {
        console.error(data.responseJSON?.message ?? 'Ошибка получения статуса DAG');
    });
};
