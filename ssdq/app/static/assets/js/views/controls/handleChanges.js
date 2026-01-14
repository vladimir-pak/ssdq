var fixed_changes = {
    dq_control_sdim: false,
    dq_control_owner_stat: false,
    dq_control_object_stat: false,
    dq_alerting_stat: false,
    dq_dag_sdim: false,
    dq_control_tags_stat: false
};

$(document).on('input change', '[data-handle-change]', 
    function(e) {
        const element = this;
        clearTimeout(element._debounceTimer);
        element._debounceTimer = setTimeout(function() {
            fixed_changes[element.getAttribute('data-handle-change')] = true;
            element._debounceTimer = null;
        }, 500);
    }
);