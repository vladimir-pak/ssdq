// показать/спрятать sql и параметры
$(document).on('click', '.js-toggle-btn', function() {
    $(this).next('div').slideToggle(300);
});

// добавление параметра
const addParam = () => {
    let ind = $(`#input-parameters .input-group`).length;
    let paramHtml = `<div class="input-group ${ind}-ind-param">
    <div class="col-lg-5">
        <input type="text" class="form-control mt-2" name="param-keys" required>
    </div>
    <div class="col-lg-6">
        <input type="text" class="form-control mt-2" name="param-values" required>
    </div>
    <div class="col-1" style="align-content: center;">
        <a onclick="removeParam(${ind})">
            <i class="nav-icon fas fa-minus fa-lg"></i>
        </a>
    </div>
    </div>`;
    $('#input-parameters').append(paramHtml);
};

// удаление параметра
const removeParam = (ind=undefined) => {
    if ($('#input-parameters .input-group').length <= 1) {
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
        $(`#input-parameters .${ind}-ind-param`).remove();
    } else {
        $('#input-parameters .input-group').last().remove();
    }
};

// функция валидации параметров в соответствии с sql
const checkParams = (params) => {
    const sql = $("#sql").val();
    // проверка на кириллицу
    const regexCyrillic = /\{[\w+]*[а-яёА-ЯË]+\}/;
    let cyrillicMatches = sql.match(regexCyrillic);
    let cntMatchs = cyrillicMatches ? cyrillicMatches.length : 0;
    if (cntMatchs > 0) {
        Swal.fire({
            icon: "error",
            title: "В параметрах должны использоваться только англ буквы",
            position: 'top-end',
            toast: true,
            showConfirmButton: false,
            timer: 3000
        });
        return false;
    };

    // прверка количества параметров и ключей параметров
    const regex = /\{(\w+)\}/g;
    const matches = [];
    let match;
    while ((match = regex.exec(sql)) !== null) {
        matches.push(match[1]);
    };
    const uniqueMatches = [...new Set(matches)];
    const cntSql = uniqueMatches ? uniqueMatches.length : 0;
    const paramsKeys = Object.keys(params);
    const cntParams = paramsKeys.length;
    if (cntParams != cntSql) {
        const msg = cntSql < cntParams ? "Параметров больше, чем заявлено в sql" : "Параметров меньше, чем заявлено в sql";
        Swal.fire({
            icon: "error",
            title: msg,
            position: 'top-end',
            toast: true,
            showConfirmButton: false,
            timer: 3000
        });
        return false;
    };
    for (e of paramsKeys) {
        if (!matches.includes(e)) {
            Swal.fire({
                icon: "error",
                title: `Параметр ${e} не найден в SQL`,
                position: 'top-end',
                toast: true,
                showConfirmButton: false,
                timer: 3000
            });
            return false;
        };
    };

    return true;
};

/* DataTable start */
const columns = [
    {data: 'id'},
    {data: 'name'},
    {data: 'description'},
    {
        data: 'deleted_flag',
        render: function (data) {
            return data == 'Y' ? 'Да' : 'Нет';
        }
    }
];

const attr = ['id', 'name', 'description', 'sql'];
const toggleActiveList = ['update', 'remove', 'hardRemove'];
const toggleDeletedList = ['restore'];
var team_id = $('#team_id').val();

var dataTab = new dataTableHandler(
    'patternSql',
    columns,
    `api/admin/pattern-sql?teamId=${team_id}`,
    'add',
    toggleActiveList,
    true,
    3,
    toggleDeletedList
);

const customFunc = () => {
    const id = $("#id").val();
    $("#input-parameters").empty();
    addParam();
    $("#sql").val("");
    if (id) {
        let url = window.location.protocol + '//' + window.location.host + '/api/admin/pattern-sql/' + $("#id").val();
        $.ajax({
            type: "GET",
            url: url,
            headers: {"X-CSRFToken": csrf_token},
            dataType: "json",
            encode: true,
            async: true
        }).done(function (data) {
            $("#sql").val(data.sql);
            const keys = Object.keys(data.params);
            const values = Object.values(data.params);
            const cntParams = keys.length;
            for (let i=0; i < cntParams - 1; i++) {
                addParam();
            };
            $('#input-parameters input[name="param-keys"]').each(function(index) {
                $(this).val(keys[index]);
            });
            $('#input-parameters input[name="param-values"]').each(function(index) {
                $(this).val(values[index]);
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
};

dataTab.setTableDelay();
dataTab.setRowHandler(attr, undefined, customFunc);

var myTable = dataTab.getTable();

/* DataTable end */

/* Ajax to back for CRUD (start) */
const requiredAttributes = ['name', 'description', 'sql'];

var postRequests = new postRequests(
    'PatternSql',
    'SQL шаблон',
    ['id', 'team_id', 'name', 'description', 'sql']
);

$('#add, #update, #remove, #hardRemove, #restore').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    let params = {};
    $('#input-parameters input[name="param-keys"]').each(function(index) {
        const value = $('#input-parameters input[name="param-values"]').eq(index).val();
        if ($(this).val() === '' || value === '') {
            Swal.fire({
                icon: "warning",
                title: "Не заполнены параметры",
                position: 'top-end',
                toast: true,
                showConfirmButton: false,
                timer: 3000
            });
            return false;
        };
        params[$(this).val()] = $('#input-parameters input[name="param-values"]').eq(index).val();
    });

    if (!checkParams(params)) {
        return false;
    };

    let formData = {
        id: $("#id").val(),
        team_id: $("#team_id").val(),
        name: $("#name").val(),
        description: $("#description").val(),
        sql: $("#sql").val(),
        params: JSON.stringify(params)
    };

    postRequests.postRequest(
        'api/admin/pattern-sql' + (this.id != "add" ? `/${$("#id").val()} `: ""), 
        this.id,
        this.id == 'hardRemove' ? 'hardDelete=True' : undefined,
        this.id == "add" ? "PUT" : undefined,
        formData
    );
    dataTab.resetButtons(attr);
    $("#input-parameters").empty();
    addParam();
    myTable.draw();
});

$('#team_id').on('change', function() {
    team_id = $(this).val();
    myTable.ajax.url(`/api/admin/pattern-sql?teamId=${team_id}`);
    toggleActiveList.forEach((e) => {dataTab.setHidden(e)});
    toggleDeletedList.forEach((e) => {dataTab.setHidden(e)});
    dataTab.removeHidden('add');
    myTable.ajax.reload();
    //myTable.draw();
});
