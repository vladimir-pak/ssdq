const gridDiv = document.querySelector("#patternSqlGrid");

const toggleActiveList = ['update', 'remove', 'hardRemove'];
const toggleDeletedList = ['restore'];

const columnDefs = [
    { headerName: "ID", field: "id", colId: "id", filter: "agTextColumnFilter" },
    { headerName: "Наименование", field: "name", colId: "name", filter: "agTextColumnFilter" },
    { headerName: "Описание", field: "description", colId: "description", filter: "agTextColumnFilter" },
    { headerName: "sql", field: "sql", colId: "sql", filter: "agTextColumnFilter", hide: true },
    { headerName: "params", field: "params", colId: "params", filter: "agTextColumnFilter", hide: true },
    {
        headerName: "Удален",
        field: "deleted_flag",
        colId: "deleted_flag",
        filter: "agTextColumnFilter",
        width: 120,
    }
];

// показать/спрятать sql и параметры
$(document).on('click', '.js-toggle-btn', function() {
    $(this).next('div').slideToggle(300);
    $(this).next('div').next('div').slideToggle(300);
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

const rowHandler = (data, event) => {
    if (data) {
        $("#input-parameters").empty();
        addParam();

        $('#id').val(data.id);
        $('#name').val(data.name);
        $('#description').val(data.description);
        $('#sql').val(data.sql);
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
    } else {
        $('#id').val('');
        $('#name').val('');
        $('#description').val('');
        $('#sql').val('');
    }

    if (event) {
        window.AGGridUtils.setHidden('add');
        deleted = data.deleted_flag == 'Y' ? true : false;

        toggleActiveList.forEach((element) => {
            deleted ? window.AGGridUtils.setHidden(element) : window.AGGridUtils.removeHidden(element);
        });
        toggleDeletedList.forEach((element) => {
            deleted ? window.AGGridUtils.removeHidden(element) : window.AGGridUtils.setHidden(element);
        });
    } else {
        toggleActiveList.forEach((element) => {
            window.AGGridUtils.setHidden(element);
        });
        toggleDeletedList.forEach((element) => {
            window.AGGridUtils.setHidden(element);
        });
        window.AGGridUtils.removeHidden('add');
    }
}

function makeDatasource() {
    return {
        getRows: async (params) => {
            try {
                const body = {
                    teamId: $("#team_id").val(),
                    startRow: params.startRow,
                    endRow: params.endRow,
                    sortModel: params.sortModel,
                    filterModel: params.filterModel,
                };

                const resp = await fetch("/api/admin/pattern-sql", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": window.csrf_token,
                    },
                    body: JSON.stringify(body),
                });

                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                const data = await resp.json();

                params.successCallback(data.rows, data.lastRow);
                params.api.setGridOption("loading", false);
            } catch (e) {
                console.error(e);
                params.failCallback();
                params.api.setGridOption("loading", false);
            }
        },
    };
}

// кнопки — на странице, чтобы URL/filename были конкретными
function wireButtons(params) {
    document.querySelector("#btnResetFilters").addEventListener("click", () => {
        params.api.setFilterModel(null);
        params.api.onFilterChanged();
        params.api.paginationGoToFirstPage();
    });

    document.querySelector("#btnResetColumns").addEventListener("click", () => {
        params.api.resetColumnState();
    });

    document.querySelector("#btnExportCsv").addEventListener("click", async () => {
        await window.AGGridUtils.exportCsvAll(params, {
            url: "/api/admin/pattern-sql/csv",
            filename: "pattern_sql.csv",
            teamId: $("#team_id").val(),
            csrfToken: window.csrf_token,
        });
    });
}

const baseOptions = window.AGGridUtils.createBaseGridOptions({
    headerComponent: HideableHeader,   // ваш компонент на этой странице
    paginationPageSize: 20,
    cacheBlockSize: 20,
    maxBlocksInCache: 5,
    onGridReady: (params) => {
        params.api.setGridOption("loading", true);
        params.api.setGridOption("datasource", makeDatasource());
        wireButtons(params);
    },
});

const gridOptions = {
    ...baseOptions,
    columnDefs,
    onRowClicked: (event) => {
        const node = event.node;
        if (node.isSelected()) {
            node.setSelected(false);
            rowHandler(null);
        } else {
            event.api.deselectAll();
            node.setSelected(true);
            rowHandler(event.data, event);
        }
    },
};

const gridApi = agGrid.createGrid(gridDiv, gridOptions);

$("#team_id").on("change", () => {
    gridApi.setGridOption("datasource", makeDatasource());
    gridApi.paginationGoToFirstPage();
});

/* Ajax to back for CRUD */
const inputAttributes = ['id', 'team_id', 'name', 'description', 'sql'];
const requiredAttributes = ['name', 'description', 'sql'];

var postRequests = new postRequests(
    'PatternSql',
    'SQL шаблон',
    inputAttributes
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
        'api/admin/pattern-sql' + (this.id != "add" ? `/${$("#id").val()} ` : ""), 
        this.id,
        this.id == 'hardRemove' ? 'hardDelete=True' : undefined,
        this.id == "add" ? "PUT" : undefined,
        formData
    );
    inputAttributes.filter(item => item !== 'team_id').forEach(e => {
        $(`#${e}`).val('');
    });
    rowHandler(null);
    gridApi.setGridOption("datasource", makeDatasource());
    gridApi.paginationGoToFirstPage();
});
