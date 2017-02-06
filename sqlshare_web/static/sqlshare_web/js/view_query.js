var prep_query_details_page = (function() {
    "use strict";
    var code_mirror;

    function create_new_dataset_from_query() {
        $("#new_query_sql").val(code_mirror.getValue());
        $("#new_dataset_from_query_form").submit();
    }

    function create_new_dataset_derive() {
        $("#new_dataset_by_derive_form").submit();
    }


    function add_events() {
        $("#run_query").on("click", function() { $("#update_dataset_sql").show(); });
        $("#new_dataset_from_query").on("click", create_new_dataset_from_query);
        // defined in run_query.js
        code_mirror = prep_polling_query();

        return code_mirror;
    }

    return add_events;
})();
