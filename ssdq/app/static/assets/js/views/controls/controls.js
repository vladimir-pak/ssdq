const weekDays = {
    1: "понедельник",
    2: "вторник",
    3: "средау",
    4: "четверг",
    5: "пятницу",
    6: "субботу",
    0: "воскресенье"
};

const printSch = () => {
    let value = document.getElementById('select_sch').value;
    if (value === 'minutes') {
        let minute = Number(document.getElementById('minute_select').value);
        document.getElementById('descForSch').innerHTML = 'Запуск каждые ' + minute + ' минут';
    };
    if (value === 'hour') {
        let minute = Number(document.getElementById('hour_select').value);
        document.getElementById('descForSch').innerHTML = 'Запуск каждый час в ' + minute + ' минут';
    };
    if (value === 'day') {
        let minute = Number(document.getElementById('time_minute_day_select').value);
        let hour = Number(document.getElementById('time_hour_day_select').value);
        document.getElementById('descForSch').innerHTML = 'Запуск каждый день в ' + hour + ':' + minute;
    };
    if (value === 'week') {
        let minute = Number(document.getElementById('time_minute_week_select').value);
        let hour = Number(document.getElementById('time_hour_week_select').value);
        let day = Number(document.getElementById('day_of_week_select').value);
        let weekDay = weekDays[day]
        document.getElementById('descForSch').innerHTML = 'Запуск каждую неделю в ' + weekDay + ' в ' + hour + ':' + minute;
    };
    if (value === 'none') {
        document.getElementById('descForSch').innerHTML = 'Не запускать';
    };
    if (value === 'month') {
        let minute = Number(document.getElementById('time_minute_month_select').value);
        let hour = Number(document.getElementById('time_hour_month_select').value);
        let day = Number(document.getElementById('day_of_month_select').value);
        document.getElementById('descForSch').innerHTML = 'Запуск каждый ' + day + ' день в месяце в ' + hour + ':' + minute;
    };
};

const selectSch = () => {
    var e = document.getElementById('select_sch');
    var value = e.value;
    var text = e.options[e.selectedIndex].text;
    var minutediv = document.getElementById('minutediv');
    var hourdiv = document.getElementById('hourdiv');
    var time_hour_day_div = document.getElementById('time_hour_day_div');
    var time_minute_day_div = document.getElementById('time_minute_day_div');
    var day_of_week_div = document.getElementById('day_of_week_div');
    var time_minute_week_div = document.getElementById('time_minute_week_div');
    var time_hour_week_div = document.getElementById('time_hour_week_div');
    if (value === 'minutes') {
        hourdiv.hidden = true;
        minutediv.hidden = false;
        time_hour_day_div.hidden = true;
        time_minute_day_div.hidden = true;
        day_of_week_div.hidden = true;
        time_minute_week_div.hidden = true;
        time_hour_week_div.hidden = true;
        day_of_month_div.hidden = true;
        time_hour_month_div.hidden = true;
        time_minute_month_div.hidden = true;
    };
    if (value === 'day') {
        hourdiv.hidden = true;
        minutediv.hidden = true;
        time_hour_day_div.hidden = false;
        time_minute_day_div.hidden = false;
        day_of_week_div.hidden = true;
        time_minute_week_div.hidden = true;
        time_hour_week_div.hidden = true;
        day_of_month_div.hidden = true;
        time_hour_month_div.hidden = true;
        time_minute_month_div.hidden = true;
    };
    if (value === 'hour') {
        hourdiv.hidden = false;
        minutediv.hidden = true;
        time_hour_day_div.hidden = true;
        time_minute_day_div.hidden = true;
        day_of_week_div.hidden = true;
        time_minute_week_div.hidden = true;
        time_hour_week_div.hidden = true;
        day_of_month_div.hidden = true;
        time_hour_month_div.hidden = true;
        time_minute_month_div.hidden = true;
    };
    if (value === 'week') {
        hourdiv.hidden = true;
        minutediv.hidden = true;
        time_hour_day_div.hidden = true;
        time_minute_day_div.hidden = true;
        day_of_week_div.hidden = false;
        time_minute_week_div.hidden = false;
        time_hour_week_div.hidden = false;
        day_of_month_div.hidden = true;
        time_hour_month_div.hidden = true;
        time_minute_month_div.hidden = true;
    };
    if (value === 'none') {
        hourdiv.hidden = true;
        minutediv.hidden = true;
        time_hour_day_div.hidden = true;
        time_minute_day_div.hidden = true;
        day_of_week_div.hidden = true;
        time_minute_week_div.hidden = true;
        time_hour_week_div.hidden = true;
        day_of_month_div.hidden = true;
        time_hour_month_div.hidden = true;
        time_minute_month_div.hidden = true;
    };
    if (value === 'month') {
        hourdiv.hidden = true;
        minutediv.hidden = true;
        time_hour_day_div.hidden = true;
        time_minute_day_div.hidden = true;
        day_of_week_div.hidden = true;
        time_minute_week_div.hidden = true;
        time_hour_week_div.hidden = true;
        day_of_month_div.hidden = false;
        time_hour_month_div.hidden = false;
        time_minute_month_div.hidden = false;
    };
    printSch();
};

$(function () {
    //Datemask dd/mm/yyyy
    $('#datemask').inputmask('dd/mm/yyyy', { 'placeholder': 'dd/mm/yyyy' });
    //Datemask2 mm/dd/yyyy
    $('#datemask2').inputmask('mm/dd/yyyy', { 'placeholder': 'mm/dd/yyyy' });
    //Money Euro
    $('[data-mask]').inputmask();

    //Bootstrap Duallistbox
    $('.duallistbox').bootstrapDualListbox();
});

// Прячет/показывает div с sql
$(document).on('click', '.js-toggle-btn', function() {
    $(this).next('div').slideToggle(300);
});

// Прослушиватель выбора sql шаблона
const sqlPatternHandler = (event) => {
    $("#input-parameters").empty();
    let url = window.location.protocol + '//' + window.location.host + '/api/admin/pattern-sql/' + event.target.value.trim();
        $.ajax({
            type: "GET",
            url: url,
            headers: {"X-CSRFToken": csrf_token},
            dataType: "json",
            encode: true,
            async: true
        }).done(function (data) {
            $("#sql_pattern").val(data.sql);
            const keys = Object.keys(data.params);
            const values = Object.values(data.params);
            const cntParams = keys.length;
            for (let i=0; i < cntParams; i++) {
                addParam('input-parameters');
            };
            $('#input-parameters input[name="param-keys"]').each(function(index) {
                $(this).val(keys[index]);
            });
            $('#input-parameters input[name="param-values"]').each(function(index) {
                $(this).attr('placeholder', values[index]);
            });
        }).fail(function (data) {
            Swal.fire({
                icon: 'error',
                title: JSON.parse(data.responseText).message,
                position: 'top-end',
                showConfirmButton: false,
                toast: true,
                timer: 5000
            });
        });
};
$("#pattern_id").on('input', sqlPatternHandler);

const htmlParamMap = {
    'input-crossdb-sql': `<div class="input-group">
        <div class="form-group">
            <label>Источник
                <select class="form-control is-valid mt-2" style="width: 20vw;"
                        data-handle-change="dq_dag_sdim"
                        name="input-source">
                        ${src_list.map(e => {return<option value="${e.name}">${e.description}</option>})}
                </select>
            </label>
            <label style="position: absolute; right: 0;">Наименование датафрейма
                <input type="text" class="form-control is-invalid mt-2" style="width: 20vw;"
                        placeholder="Название датафрейма в главном запросе"
                        data-handle-change="dq_dag_sdim"
                        name="input-src-name">
            </label>
        </div>
        <div class="form-group" style="width: 100%;">
            <button type="button" class="btn btn-block btn-default js-toggle-btn" 
                data-target="div-input-sql">Запрос</button>
            <div class="mb-3" style="width: 100%;" name="div-input-sql">
                <textarea class="form-control is-invalid" rows="10"
                    data-handle-change="dq_dag_sdim"
                    name="input-sql"></textarea>
            </div>
        </div>
    </div>`,
    'input-parameters': `
    <div class="input-group">
        <div class="col-lg-6">
            <input type="text" class="form-control mt-2" name="param-keys" readonly>
        </div>
        <div class="col-lg-6">
            <input type="text" class="form-control is-invalid mt-2" name="param-values">
        </div>
    </div>`
};

const addParam = (divId) => {
    const paramHtml = htmlParamMap[divId];
    $(`#${divId}`).append(paramHtml);
    addDivListeners(divId);
};

const removeParam = (divId) => {
    if ($(`#${divId} .input-group`).length > 1) {
        $(`#${divId} .input-group`).last().remove();
    } else {
        Swal.fire({
            icon: "warning",
            title: "Невозможно удалить последнее поле",
            position: 'top-end',
            toast: true,
            showConfirmButton: false,
            timer: 3000
        });
    };
};

const deleteSpec = () => {
    Swal.fire({
        title: 'Вы уверены?',
        text: "",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Да',
        cancelButtonText: 'Отменить'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                type: "DELETE",
                url: window.location.protocol + '//' + window.location.host + `/controls/${controlId}`,
                headers: {"X-CSRFToken": csrf_token},
                encode: true,
                async: false
            }).fail(function (data) {
                Swal.fire({
                    icon: 'error',
                    title: data.responseText,
                    position: 'top-end',
                    showConfirmButton: false,
                    toast: true,
                    timer: 3000
                });
            });
            Swal.fire(
                'Контроль удален!',
                '',
                'success'
            );
            setTimeout(() => {
                let url = window.location.protocol + '//' + window.location.host  + `/controls`;
                window.location.href = url;
            }, 1500);
        };
    });
};

const actualize = () => {
    $.ajax({
        type: "PUT",
        url: window.location.protocol + '//' + window.location.host + `/controls/${controlId}`,
        headers: {"X-CSRFToken": csrf_token},
        encode: true,
        async: false
    }).fail(function (data) {
        Swal.fire({
            icon: 'error',
            title: data.responseText,
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
    });

    location.reload();
}

$(document).ready(
    function() {
        printSch();
        selectSch();
        $("#pdag").toggle();
    }
);

$('#source_id').on('change', function() {
    $('#source').val(this.value);
    $('#source_pattern').val(this.value);
});

