const redirectCotrol = (action) => {
    let id = $('#controlId').val();
    if (id == '0' & action !== 'create') {
        Swal.fire({
            icon: 'error',
            title: 'Выберите контроль!',
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
    } else {
        let url;
        if (action == "show") {
            url = `/controls?id=${id}`;
        } else if (action == "update") {
            url = `/controls/${id}`;
        } else if (action == "clone") {
            url = `/controls/${id}/clone`;
        } else if (action == "report") {
            url = `/report/${id}`;
        } else if (action == "create") {
            url = `/controls/create`;
        }else {
            url = `/controls?id=${id}`;
        };
        location.assign(url);
    };
};

$('#controlId').on('change', function() {
    let id = $(this).val();
    let url;
    if (id == 0) {
        url = '/controls';
    } else {
        url = `/controls?id=${id}`;
    }
    location.assign(url);
});
