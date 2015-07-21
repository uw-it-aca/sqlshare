var prep_run_query_page = (function() {
    "use strict";

    function add_events() {
        return prep_polling_query();
    }

    return add_events;
})();


var prep_polling_query = (function() {
    "use strict";
    var current_process = null,
        current_timeout = null,
        current_delay = null,
        codemirror = null;

    function start_query() {
        //var sql = $("#query_sql").val();
        var sql = codemirror.getValue();

        if (current_process) {
            current_process.abort();
        }
        if (current_timeout) {
            window.clearTimeout(current_timeout);
        }

        show_polling_query_elements();

        reset_polling_delay();
        current_process = $.ajax({
            type: "POST",
            url: "/run_query/",
            data: {
                "sql": sql,
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
            success: handle_polling,
        });
    }

    function show_polling_query_elements() {
        $("#query_preview_panel").show();
        $("#original_results_panel").hide();

        $("#query_results_panel").hide();
        $("#query_actions_panel").hide();
        $("#query_running_panel").show();
    }

    function start_preview_polling(query_id) {
        show_polling_query_elements();
        current_timeout = window.setTimeout(function() {
            current_process = $.ajax({
                type: "GET",
                url: "/query/"+query_id,
                success: handle_polling,
            });
        }, get_next_polling_delay());

    }

    function handle_polling(data, status, xhr) {
        current_process = null;
        if (xhr.status == 202) {
            current_timeout = window.setTimeout(function() {
                var location = xhr.getResponseHeader("Location");
                current_process = $.ajax({
                    type: "GET",
                    url: location,
                    success: handle_polling,
                });
            }, get_next_polling_delay());

            return;
        }
        $("#query_results_panel").html(xhr.responseText);
        $("#query_running_panel").hide();
        $("#query_results_panel").show();
    }

    function reset_polling_delay() {
        current_delay = 50;
    }

    function get_next_polling_delay() {
        if (current_delay < 2000) {
            current_delay = current_delay * 1.5;
        }

        return current_delay;
    }

    function add_events(code_mirror, preview_query_id) {
        codemirror = code_mirror;

        console.log("Initial query id: ", preview_query_id);
        $("#run_query").on("click", start_query);

        codemirror = CodeMirror.fromTextArea(document.getElementById("query_sql"), {
            textWrapping: false,
            autoMatchParens: true,
            mode:  "text/x-mssql",
            lineNumbers: true,
            smartIndent: true,
            extraKeys: {
                Tab: false
            }
        });

        codemirror.focus();

        // This handles the case where a file is uploaded, and the preview isn't finished
        // when the page loads.
        if (preview_query_id) {
            start_preview_polling(preview_query_id);
        }

        return codemirror;
    }

    return add_events;
})();

