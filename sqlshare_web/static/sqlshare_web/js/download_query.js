var prep_download = (function() {
    "use strict";
    var codemirror;

    function add_events(code_mirror) {
        codemirror = code_mirror;
        $("#download_query").on("click", start_download);
    }

    function start_download() {
        var sql = codemirror.getValue();

        $.ajax({
            type: "POST",
            url: "/run_download/",
            data: {
                "sql": sql,
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
            success: create_download_iframe,
        });
    }

    function create_download_iframe(data, status, xhr) {
        if (xhr.status == 202) {
            var location = xhr.getResponseHeader("Location");
            $("#download_container").html(create_dl_iframe(location));
            return;
        }
    }

    function create_dl_iframe(url) {
        var frame = $('<iframe>');

        frame.attr('src', url);
        frame.attr('height', "1px");
        frame.attr('width', "1px");
        return frame;
    }

    return add_events;

})();
