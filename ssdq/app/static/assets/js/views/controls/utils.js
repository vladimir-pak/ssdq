const divToggle = (divHide, divShow) => {
    $('#'+divHide).hide();
    $('#'+divShow).show();
};

const showDiv = (divName) => {
    $('#'+divName).toggle();
};

const validText = (el) => {
    var f = document.getElementById(el);
    f.addEventListener(
        'keyup', (event) => {
            if (f.value.trim() === '') {
                f.classList.remove('is-valid');
                f.classList.add('is-invalid');
            } else {
                f.classList.remove('is-invalid');
                f.classList.add('is-valid');
            };
        }
    );
};

const validSelect = (el) => {
    var f = document.getElementById(el);
    f.addEventListener(
        'change', (event) => {
            if (f.value === '0' || f.value === '') {
                f.classList.remove('is-valid');
                f.classList.add('is-invalid');
            } else {
                f.classList.remove('is-invalid');
                f.classList.add('is-valid');
            };
        }
    );
};

const validDiv = (divId, elemId) => {
    let div = $('#' + divId);
    let f = $('#' + elemId);
    if (f.val() === '0' || f.val() === '' || f.val().length == 0) {
        div.removeClass("div-is-valid");
        div.addClass("div-is-invalid");
    } else {
        div.removeClass("div-is-invalid");
        div.addClass("div-is-valid");
    };
};

const getSelect2 = (elem, entity) => {
    var url = window.location.protocol + '//' + window.location.host;
    $('#'+elem).select2({
        minimumInputLength: 3,
        language: {
            inputTooShort: function(args) {
                return `Введите как минимум ${args.minimum} символа`
            }
        },
        ajax: {
            delay: 300,
            url: `${url}/api/select2`,
            dataType: 'json',
            data: function(params) {
                return {
                    entity: entity,
                    search: params.term || "",
                    page: params.page || 1
                }
            },
            processResults: function (data) {
                return {
                    results: data.results,
                    pagination: {
                        more: data.pagination.more == 'true'
                    }
                };
            }
        }
    });
};

$(document).ready(function() {
    getSelect2('owner_id', 'users');
    getSelect2('object_id', 'objects');
    getSelect2('alerting', 'users');
    getSelect2('pattern_id', 'pattern');
    getSelect2('tag_id', 'tags');
    $("#pattern_id").data('select2').$container.addClass('mt-2')
    $("#pattern_id").data('select2').$selection.css('min-height', '38px');
    $("#pattern_id").data('select2').$selection.addClass('form-control');
    //$("#pattern_id").data('select2').$selection.addClass('mt-2');
    //$("#pattern_id").data('select2').$selection.addClass('form-control')
    // $("#pattern_id").data('select2').$dropdown.addClass('form-control')
});