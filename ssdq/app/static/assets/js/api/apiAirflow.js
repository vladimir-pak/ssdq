const resultTranslate = {
    success: "Выполнен",
    queued: "В очереди",
    running: "Выполняется",
    failed: "Ошибка выполнения"
};


const statusTranslate = {
    enabled: "Активен",
    disabled: "Отключен"
}


$('#triggerDag, #killDag, #pauseDag, #unpauseDag, #statusDag').on('click', function() {
    const successMessageMap = {
        triggerDag: 'DAG добавлен в очередь',
        killDag: 'DAG успешно остановлен',
        pauseDag: 'Dag успешно выключен',
        unpauseDag: 'Dag успешно включен'
    };

    var endpoint = $(this).attr('id');
    var controlId = $('#controlId').val() ? $('#controlId').val() : window.controlId;

    if (controlId && controlId != 0) {
        $.ajax({
            type: "POST",
            url: `/api/dags/${endpoint}?id=${controlId}`,
            headers: {"X-CSRFToken": csrf_token},
            dataType: "json",
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
            Swal.fire({
                icon: 'error',
                title: data.responseJSON.message,
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
});