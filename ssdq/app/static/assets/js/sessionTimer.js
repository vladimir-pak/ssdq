var sessionLifetime = $('#sessionLifetime').val();

var dateSession = new Date(sessionLifetime);
var dateRus = dateSession.toLocaleString("ru");
$('#sessionLifetime').val(dateRus);

var now = new Date();
var expiring_time = Math.abs(dateSession - new Date());

const refreshSession = () => {
    $.ajax({
        type: "POST",
        url: window.location.protocol + '//' + window.location.host + '/session/refresh',
        processData: false,
        contentType: false,
        headers: {"X-CSRFToken": csrf_token},
        async: true
    }).done(function(data) {
        console.log(data)
        dateSession = new Date(data.lifetime);
        dateRus = dateSession.toLocaleString("ru");
        $('#sessionLifetime').val(dateRus);
    });
};

setTimeout(function() {
    Swal.fire({
        icon: 'warning',
        title: 'Истекает время сессии!',
        text: 'Сохраните изменения',
        position: 'top-end',
        confirmButtonText: 'Продлить',
        toast: true,
        timer: 119000
    }).then((result) => {
        if (result.isConfirmed) {
            refreshSession();
            Swal.fire({
                icon: 'success',
                title: 'Сессия продлена',
                position: 'top-end',
                toast: true,
                timer: 3000
            });
        };
    });
}, expiring_time - 119000);

setTimeout(function() {
    Swal.fire({
        icon: 'warning',
        title: 'Время сессии истекло!',
        html: 'Для повторной авторизации <br>нажмите OK',
        showConfirmButton: true,
        allowOutsideClick: true
    }).then(function(result) {
        window.location.href = window.location.protocol + '//' + window.location.host;
    });
}, expiring_time);
