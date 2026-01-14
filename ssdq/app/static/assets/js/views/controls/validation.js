// Логика валидации заполнения атрибутов в карточке контроля

// обработчик событий (проверка на заполненность полей)
const handleInput = (event) => {
    if (event.target.value.trim() === '') {
        $(event.target).removeClass('is-valid').addClass('is-invalid');
    } else {
        $(event.target).removeClass('is-invalid').addClass('is-valid');
    };
};

const handleInputForDiv = (event) => {
    if (event.target.value.trim() === '') {
        $(event.target).parent().removeClass('div-is-valid').addClass('div-is-invalid');
    } else {
        $(event.target).parent().removeClass('div-is-invalid').addClass('div-is-valid');
    };
}; 

addDivListeners = (divId) => {
    $(`#${divId}`).find("input, select, textarea")
        .on('input', handleInput)
        .on('change', handleInput)
        .on('focus', handleInput);
};

addIdListeners = (id) => {
    $(`#${id}`)
        .on('input', handleInput)
        .on('focus', handleInput);
};

addIdListenersForDiv = (id) => {
    $(`#${id}`)
        .on('input', handleInputForDiv)
        .on('focus', handleInputForDiv);
};

// атрибуты для валидации на 1 странице
const firstPageAttributes = [
    "control_name",
    "status_id",
    "team_id",
    //"owner_id",
    "segment_id",
    "source_id",
    "conditions",
    "description",
    //"object_id",
    "threshold_min",
    "threshold_max"
];

// атрибуты для валидации на 2 странице
const dagAttributes = {
    "#simple-control": "input-simple",
    "#crossdb-control": "input-crossdb",
    "#pattern-control": "input-pattern"
}

// атрибуты с multi-select
const multiSelectDiv = [
    "owner_id",
    "object_id"
]

$(document).ready(function() {
    for (id of firstPageAttributes) {
        addIdListeners(id);
    };

    for (id of multiSelectDiv) {
        addIdListenersForDiv(id);
    };

    for (div of Object.values(dagAttributes)) {
        addDivListeners(div);
    };
});

// функционал по проверке заполненности полей
const showErrorFillMessage = () => {
    return Swal.fire({
        icon: 'error',
        title: 'Заполните все обязательные поля!',
        position: 'top-end',
        showConfirmButton: false,
        toast: true,
        timer: 3000
    });
};

const pageToggle = () => {
    $(`#pdag, #pcard`).toggle();
};

const checkFill = (pageNumber, save=false) => {
    if (pageNumber == 1) {
        for (id of firstPageAttributes) {
            if ($(`#${id}`).val() == null || $(`#${id}`).val().trim() === '') {
                showErrorFillMessage();
                return false;
            };
        };

        for (id of multiSelectDiv) {
            if ($(`#${id}`).val().length <= 0) {
                showErrorFillMessage();
                return false;
            };
        };
        if (!save) {
            pageToggle();
        };
        return true;
    } else if (pageNumber == 2) {
        const hrefDagType = $("#panels li .nav-link.active").attr('href');
        let checked = true;
        $(`#${dagAttributes[hrefDagType]}`).find("input, select, textarea")
            .each(function() {
                if ($(this).val() == null || $(this).val().trim() === '') {
                    checked = false;
                    return false;
                };
            });
        if (!checked) {
            showErrorFillMessage();
            return false;
        };
        return true;
    } else {
        console.log("Entered incorrent page number")
        return false;
    };
};