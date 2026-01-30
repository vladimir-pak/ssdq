const modalToggle = () => {
    $('#modal-loading').modal('toggle');
};

var savedSpec = false;

const EXCLUDE_INPUTS = new Set([
    "input-source", 
    "input-sql",
    "input-src-name",
    "source-pattern",
    "sql-pattern",
    "param-keys",
    "param-values",
    "customRadio",
    "created_by"
]);

const INCLUDE_TYPES = new Set([
    "select-one",
    "select-multiple",
    "text",
    "textarea",
    "number"
]);

const saveSpec = (onlySpec) => {
    if (!onlySpec && !checkFill(2, true)) {
        return false;
    } else if (onlySpec && !checkFill(1, true)) {
        return false;
    };
    modalToggle();
    let formData = {};
    let formElements = [...document.querySelector('form').elements].filter(element => (INCLUDE_TYPES.has(element.type) && !EXCLUDE_INPUTS.has(element.name)));
    formElements.forEach(element => {
        formData[element.name] = element.value ? element.value : undefined;
    });
    formData['onlySpec'] = onlySpec;
    formData['owner_id'] = $('#owner_id').val();
    formData['object_id'] = $('#object_id').val();
    formData['tag_id'] = $('#tag_id').val();
    formData['tag_id'] = formData['tag_id'].filter(item => item);
    formData['alerting'] = $('#alerting').val();
    formData['limit'] = $('#limit').prop('checked');

    // Кастомные атрибуты карточки контроля
    let params = {};
    $('#input-attributes select[name="param-keys"]').each(function(index) {
        const value = $('#input-attributes input[name="param-values"]').eq(index).val();
        const key = $(this).val();
        if (key === '' || value === '') {
            Swal.fire({
                icon: "warning",
                title: "Не заполнены выбран атрибут карточки контроля",
                position: 'top-end',
                toast: true,
                showConfirmButton: false,
                timer: 3000
            });
            return false;
        };
        params[key] = value;
    });

    formData['team_attributes'] = JSON.stringify(params);

    // Запись изменений по сущностям (fixed_changes - из handleChanges.js)
    Object.assign(formData, fixed_changes);
    
    let url = document.URL.split('/');
    let endpoint = url[url.length - 1];
    let curUrl = endpoint == 'create' ? '/controls/create' : 
        endpoint == 'clone' ? '/controls/create' : `/controls/${controlId}`

    if (curUrl == '/controls/create' && savedSpec) {
        curUrl = ('/controls/' + controlId);
        formData['dq_control_sdim'] = true;
        formData['dq_control_owner_stat'] = true;
        formData['dq_control_object_stat'] = true;
        formData['dq_alerting_stat'] = true;
        formData['dq_dag_sdim'] = true;
    };

    // Определение типа дага
    const dagTypeMap = {
        "#simple-control": "SIMPLE",
        "#crossdb-control": "CROSSDATABASE",
        "#pattern-control": "PATTERN"
    }
    const hrefDagType = $("#panels li .nav-link.active").attr('href');
    formData["dagType"] = dagTypeMap[hrefDagType];

    if (dagTypeMap[hrefDagType] == 'PATTERN') {
        // сбор параметров для шаблонизированного контроля
        let params = {};
        $('#input-parameters input[name="param-keys"]').each(function(index) {
            const value = $('#input-parameters input[name="param-values"]').eq(index).val();
            if (value === '') {
                return false;
            };
            params[$(this).val()] = value;
        });
        formData["params"] = params;
    } else if (dagTypeMap[hrefDagType] == 'CROSSDATABASE') {
        // Сбор параметров для кроссбазового контроля
        let params = [];
        $('#input-crossdb-sql select[name="input-source"]').each(function(index) {
            let source = {"source": $(this).val()};
            const src_name = $('#input-crossdb-sql input[name="input-src-name"]').eq(index).val();
            if ($(this).val() === '') {
                return false;
            };
            source["source_name"] = src_name;
            const sql = $('#input-crossdb-sql textarea[name="input-sql"]').eq(index).val();
            if ($(this).val() === '') {
                return false;
            };
            source["sql"] = sql;
            params.push(source);
        });
        formData["params"] = params;
    } else {
        formData["params"] = undefined;
    };

    $.ajax({
        type: "POST",
        url: window.location.protocol + '//' + window.location.host + curUrl,
        dataType: "json",
        data: JSON.stringify(formData),
        headers: {"X-CSRFToken": csrf_token, "Content-Type": "application/json"},
        encode: true,
        async: false
    }).done(function (data) {
        if (curUrl == '/controls/create' && controlId == 0) {
            controlId = data.control_id;
        };

        if (onlySpec) {
            Swal.fire({
                icon: 'success',
                title: 'Карточка контроля сохранена',
                position: 'top-end',
                showConfirmButton: false,
                toast: true,
                timer: 3000
            });
        } else {
            window.location.href = window.location.protocol + '//' + window.location.host + `/controls?id=${controlId}`;
        };

        savedSpec = true;
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
    setTimeout(modalToggle, 1000);
    return ;
};
