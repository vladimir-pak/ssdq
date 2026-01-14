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

const attr = ['id', 'name', 'description'];
const toggleActiveList = ['update', 'remove', 'hardRemove'];
const toggleDeletedList = ['restore'];
var team_id = $('#team_id').val();

var dataTab = new dataTableHandler(
    'errorReason',
    columns,
    `api/admin/error-reason?teamId=${team_id}`,
    'add',
    toggleActiveList,
    true,
    3,
    toggleDeletedList
);
dataTab.setTableDelay();
dataTab.setRowHandler(attr);

var myTable = dataTab.getTable();

/* DataTable end */

/* Ajax to back for CRUD (start) */
const requiredAttributes = ['name', 'description'];

var postRequests = new postRequests(
    'ErrorReason',
    'Причина ошибки',
    ['id', 'team_id', 'name', 'description']
);

$('#add, #update, #remove, #hardRemove, #restore').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    postRequests.postRequest(
        'api/admin/error-reason' + (this.id != "add" ? `/${$("#id").val()}` : ""), 
        this.id,
        this.id == 'hardRemove' ? 'hardDelete=True' : undefined,
        this.id == "add" ? "PUT" : undefined
    );
    dataTab.resetButtons(attr);
    myTable.draw();
});

$('#team_id').on('change', function() {
    team_id = $(this).val();
    myTable.ajax.url(`/api/admin/error-reason?teamId=${team_id}`);
    toggleActiveList.forEach((e) => {dataTab.setHidden(e)});
    toggleDeletedList.forEach((e) => {dataTab.setHidden(e)});
    dataTab.removeHidden('add');
    myTable.ajax.reload();
    //myTable.draw();
});
