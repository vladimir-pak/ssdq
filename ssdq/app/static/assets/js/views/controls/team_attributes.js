/* Utils */
const apiData = (endpoint, method="GET", body=undefined) => {
    let url = window.location.protocol + '//' + window.location.host + '/api/' + endpoint;
    var response;
    $.ajax({
        type: method,
        url: url,
        data: body,
        headers: {"X-CSRFToken": csrf_token},
        dataType: "json",
        encode: true,
        async: false
    }).done(function (data) {
        response = data;
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

    return response;
};

const teamAttributes = apiData("controls/team-attributes/"+$("#team_id").val());
const maxAttributes = teamAttributes.length;
var requiredAttributes = 0;

const getOption = (key) => {
    return `<option value="${key}">${key}</option>`;
};
var optionsHtml = teamAttributes
    .map(e => !e.is_required ? getOption(e.key) : null)
    .join('');

// добавление параметра
const addAttribute = () => {
    if ($('#input-attributes .input-group').length >= maxAttributes) {
        Swal.fire({
            icon: "warning",
            title: "Достигнуто максимальное значение атрибутов",
            position: 'top-end',
            toast: true,
            showConfirmButton: false,
            timer: 3000
        });
        return;
    }
    let ind = $(`#input-attributes .input-group`).length;
    let paramHtml = `<div class="input-group ${ind}-ind-param">
        <div class="col-lg-5">
            <select class="form-control mt-2" name="param-keys" required data-handle-change="dq_control_sdim">
                ${optionsHtml}
            </select>
        </div>
        <div class="col-lg-6">
            <input type="text" class="form-control mt-2" name="param-values" required 
                data-handle-change="dq_control_sdim">
        </div>
        <div class="col-1" style="align-content: center;">
            <a onclick="removeAttr(${ind})">
                <i class="nav-icon fas fa-minus fa-lg"></i>
            </a>
        </div>
    </div>`;
    $('#input-attributes').append(paramHtml);
};

// удаление параметра
const removeAttr = (ind=undefined) => {
    if ($('#input-attributes .input-group').length <= requiredAttributes) {
        Swal.fire({
            icon: "warning",
            title: "Невозможно удалить последнее поле",
            position: 'top-end',
            toast: true,
            showConfirmButton: false,
            timer: 3000
        });
        return;
    }

    if (ind !== undefined) {
        $(`#input-attributes .${ind}-ind-param`).remove();
    } else {
        $('#input-attributes .input-group').last().remove();
    }
};
/* Utils */
const path = window.location.pathname;
const pathParts = path.split('/').filter(part => part.length > 0);
const endpoint = pathParts[pathParts.length - 1];

const setDefaultAttributes = () => {
    let ind = 0;
    teamAttributes
        .filter(e => e.is_required)
        .forEach(e => {
            let paramHtml = `
                <div class="input-group ${ind}-ind-param">
                    <div class="col-lg-5">
                        <select class="form-control mt-2" name="param-keys" required readonly>
                            <option value="${e.key}">${e.key}</option>
                        </select>
                    </div>
                    <div class="col-lg-6">
                        <input type="text" class="form-control mt-2" name="param-values" 
                            data-handle-change="dq_control_sdim" required
                            placeholder="${e.description}" value="${endpoint !== 'create' ? (filledAttributes?.[e.key] ?? '') : ''}">
                    </div>
                </div>`;
            $('#input-attributes').append(paramHtml);
            ind++;
            requiredAttributes++;
        });
    if (endpoint !== 'create') {
        teamAttributes
            .filter(e => !e.is_required & e.key in filledAttributes)
            .forEach(e => {
                let optionsHtml = teamAttributes
                    .filter(el => !el.is_required && el.key !== e.key)
                    .map(({ key }) => getOption(key))
                    .join('');
                let paramHtml = `
                    <div class="input-group ${ind}-ind-param">
                        <div class="col-lg-5">
                            <select class="form-control mt-2" name="param-keys" required
                                data-handle-change="dq_control_sdim">
                                <option value="${e.key}" selected>${e.key}</option>
                                ${optionsHtml}
                            </select>
                        </div>
                        <div class="col-lg-6">
                            <input type="text" class="form-control mt-2" name="param-values" required
                                data-handle-change="dq_control_sdim"
                                placeholder="${e.description}" value="${filledAttributes[e.key]}">
                        </div>
                        <div class="col-1" style="align-content: center;" data-handle-change="dq_control_sdim">
                            <a onclick="removeAttr(${ind})">
                                <i class="nav-icon fas fa-minus fa-lg"></i>
                            </a>
                        </div>
                    </div>`;
                $('#input-attributes').append(paramHtml);
                ind++;
            });
    }
};

setDefaultAttributes();

