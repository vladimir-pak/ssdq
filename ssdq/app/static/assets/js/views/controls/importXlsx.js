const modalToggle = () => {
    $('#modal-loading').modal('toggle');
};

var table;

$("#xlsxFile").on("change", function(event) {
    const fileName = event.target.files[0] ? event.target.files[0].name : "Добавить xlsx";
    $(this).next('.custom-file-label').text(fileName);

    if (event.target.files[0]) {
        $(this).next('.custom-file-label').addClass('file-selected');
    } else {
        $(this).next('.custom-file-label').removeClass('file-selected');
    };
});

$("#modalImportButton").on("click", function() {
    if (table) return;
    table = new DataTable("#import-result", {
        language: {
            url: '/static/assets/ru.json'
        },
        processing: true,
        lengthMenu: [[10, 25, 50], [10, 25, 50]],
        searching: true,
        autoWidth: false,
        oLanguage: {
            sProcessing: '<div class="spinner-border text-success" style="width: 6rem; height: 6rem;"></div>',
            sEmptyTable: 'Нет данных'
        }
    });
    return;
});

const parseXlsxFile = (file) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = function(e) {
            try {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array' });

                // Получаем первый лист
                const firstSheet = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[firstSheet];

                // Конвертируем в JSON
                const jsonData = XLSX.utils.sheet_to_json(worksheet);
                
                // Преобразуем в массив
                const resultArray = jsonData.map(row => {
                    const dict = {};
                    for (const [key, value] of Object.entries(row)) {
                        dict[key] = value;
                    }
                    return dict;
                });
                resolve(resultArray)
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: "Ошибка при парсинге файла",
                    text: error,
                    position: 'top-end',
                    showConfirmButton: false,
                    toast: true,
                    timer: 3000
                });
                reject(error);
            }
        };

        reader.onerror = function() {
            Swal.fire({
                icon: 'error',
                title: "Ошибка при чтении файла",
                position: 'top-end',
                showConfirmButton: false,
                toast: true,
                timer: 3000
            });
            reject(new Error('Ошибка при чтении файла'));
        };

        reader.readAsArrayBuffer(file);
    });
};

$("#import-xlsx-button").on("click", async function() {
    const fileInput = $("#xlsxFile")[0];
    const file = fileInput.files[0];
    const validExtensions = [".xlsx"];

    if (!file) {
        Swal.fire({
            icon: 'error',
            title: "Не выбран файл",
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
        return;
    };

    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!validExtensions.includes(fileExtension)) {
        Swal.fire({
            icon: 'error',
            title: "Допустимы только xlsx",
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
        return;
    };

    modalToggle();

    const parsedData = await parseXlsxFile(file);
    let formData = JSON.stringify(parsedData);

    $.ajax({
        type: "POST",
        url: window.location.protocol + '//' + window.location.host + '/import/controls',
        data: formData,
        processData: false,
        headers: {
            "X-CSRFToken": csrf_token,
            "Content-Type": "application/json"
        },
        async: false
    }).done(function (data) {
        Swal.fire({
            icon: 'success',
            title: 'Файл успешно обработан',
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
        table.clear();
        
        const rowData = data.data.map(item => [
            (item.index + 1),
            item.control_name,
            item.status,
            item.message
        ]);
        table.rows.add(rowData).draw();
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
});