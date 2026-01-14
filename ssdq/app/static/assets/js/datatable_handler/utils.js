window.postRequests = class PostRequests {
    static class_operations = ['#add', '#update', '#remove', '#hardRemove', '#restore'];
    static messages = [' добавлен(а)', ' изменен(а)', ' удален(а)', ' удален(а) навсегда', ' восстановлен(а)']
    
    /**
     * 
     * @param {string} entity [entity name in CamelCase format]
     * @param {string} entityRus [russian entity name]
     * @param {Array<string>} attributes [List of attributes from POST form]
     */
    constructor (
        entity, //CamelCase
        entityRus,
        attributes //array
    ) {
        this.url = window.location.protocol + '//' + window.location.host + '/';
        this.entity = entity;
        this.operations = PostRequests.class_operations;
        PostRequests.class_operations.forEach((e, i) => {
            this.operations[i] += entity;
        });
        this.buttonsIdString = this.operations.join();

        this.successMessages = {};
        PostRequests.class_operations.forEach((e, i) => {
            this.successMessages[e.slice(1)] = entityRus + PostRequests.messages[i];
        });

        this.attributes = attributes;
        this.entityRus = entityRus;
    };

    /**
     * 
     * @param {Array<string>} requiredFields [List of fields ID for post request]
     * @returns {boolean} true if all fields are filled, false if any fields has not filled
     */
    verifyFileds(requiredFields) {
        let verified = true;
        requiredFields.forEach((e) => {
            let value = $('#' + e).val();
            if (value == 'null' || value == '' || value == undefined) {
                Swal.fire({
                    icon: 'error',
                    title: 'Не заполнены обязательные поля',
                    position: 'top-end',
                    showConfirmButton: false,
                    toast: true,
                    timer: 5000
                });
                verified = false;
                return false;
            };
        });
        return verified;
    };

    /**
     * 
     * @param {string} endpoint [button's Id = endpoint]
     * @param {string} buttonId [add, update, remove, hardRemove, restore]
     * @param {string} params [http request params without ? ]
     * @returns undefined
     */
    postRequest(
        endpoint,
        buttonId,
        params=undefined,
        method=undefined,
        body=undefined
    ) {
        let data = {};
        let formData = {};
        this.attributes.forEach((e) => {
            data[e] = $(`#${e}`).val();
        });
        if (body) {
            formData = Object.assign({}, data, body);
        } else {
            formData = data;
        };
        let successMessages = this.successMessages;
        let entityRus = this.entityRus;
        let entity = this.entity;
        let methodMap = {
            add: 'POST',
            update: 'PATCH',
            remove: 'DELETE',
            hardRemove: 'DELETE',
            restore: 'PUT'
        };

        $.ajax({
            type: method ? method : methodMap[buttonId],//"POST",
            url: `${this.url + endpoint}${params ? `?${params}` : ''}`,
            data: formData,
            headers: {"X-CSRFToken": csrf_token},
            dataType: "json",
            encode: true,
            async: false
        }).done(function (data) {
            if (data === undefined && entityRus) {
                Swal.fire({
                    icon: 'success',
                    title: successMessages[buttonId + entity],
                    position: 'top-end',
                    showConfirmButton: false,
                    toast: true,
                    timer: 5000
                });
            };
        }).fail(function(data) {
            try {
                Swal.fire({
                    icon: 'error',
                    title: JSON.parse(data.responseText).message,
                    position: 'top-end',
                    showConfirmButton: false,
                    toast: true,
                    timer: 5000
                });
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Произошла непредвиденная ошибка',
                    position: 'top-end',
                    showConfirmButton: false,
                    toast: true,
                    timer: 5000
                });
            };
        });

        return;
    };
};
