
/* DataTable start */
const columns = [
    {
        data: 'name',
        render: function (data, type, row) {
            return `<a href="/admin/teams/${row.id}">${data}</a>`
        }
    },
    {data: 'display_name'},
    {data: 'description'},
    {data: 'jira_project'},
    {data: 'id'},
];

const attr = ['name', 'description', 'display_name', 'jira_project', 'id'];
const toggleActiveList = ['hardRemove', 'edit'];

var dataTab = new dataTableHandler(
    'teams',
    columns,
    `api/admin/teams`,
    'add',
    toggleActiveList
);
dataTab.setTableDelay();

const customFunc = () => {
    if ($("#teams tbody").find('tr.selected').length) {
        $("#name, #description, #display_name, #jira_project").prop("readonly", true);
    } else {
        $("#name, #description, #display_name, #jira_project").prop("readonly", false);
    };
};

dataTab.setRowHandler(attr, undefined, customFunc);

var myTable = dataTab.getTable();

/* DataTable end */

/* Ajax to back for CRUD (start) */
const requiredAttributes = ['name', 'description', 'display_name', 'jira_project'];

var postRequests = new postRequests(
    'Teams', // entity name
    'Команда', // russian entity name
    ['id', 'name', 'display_name', 'description', 'jira_project'] // list of inputs (create form to http request)
);

$('#add, #hardRemove').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    postRequests.postRequest(
        `api/admin/teams` + (this.id == "hardRemove" ? `/${$("#id").val()}` : ""),
        this.id,
        undefined,
        this.id == "add" ? "PUT" : "DELETE"
    );
    dataTab.resetButtons(attr);
    myTable.draw();
});

$("#edit").on("click", function() {
    location.href=`/admin/teams/${$("#id").val()}`;
});
