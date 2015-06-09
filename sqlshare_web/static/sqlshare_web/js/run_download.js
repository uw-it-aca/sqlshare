var prep_run_download_page = (function() {
    "use strict";
    var current_process = null,
        current_timeout = null,
        current_delay = null,
        codemirror = null;

    function start_download() {
        //var sql = $("#query_sql").val();
        sql = codemirror.getValue();

        if (current_process) {
            current_process.abort();
        }
        if (current_timeout) {
            window.clearTimeout(current_timeout);
        }
        
        $("#query_preview_panel").show();
        
        $("#query_results_panel").hide();
        $("#query_actions_panel").hide();
        $("#query_running_panel").show();

        reset_polling_delay();
        current_process = $.ajax({
            type: "POST",
            url: "/run_download/",
            data: {
                "sql": sql,
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
            success: handle_polling,
        });
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
        var download_uri = xhr.responseText;

        $("#download_container").html(create_dl_iframe(download_uri));

    }

    function create_dl_iframe(url) {
        var frame = $('<iframe>');

        frame.attr('src', url);
        frame.attr('height', "1px");
        frame.attr('width', "1px");
        return frame;

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

    function add_events() {
        $("#download_query").on("click", start_download);

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
    }

    return add_events;
})();
