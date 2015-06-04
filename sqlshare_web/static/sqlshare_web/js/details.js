var prep_details_page = (function() {
    "use strict";
    var last_description,
        code_mirror;

    function add_code_mirror() {
        // work around jshint - newcap error.
        var func_code_mirror = CodeMirror;
        var codemirror = CodeMirror.fromTextArea(document.getElementById("dataset_sql"), {
            textWrapping: false,
            autoMatchParens: true,
            mode:  "text/x-mssql",
            lineNumbers: true,
            smartIndent: true,
            extraKeys: {
                Tab: false
            }
        });

        return codemirror;
    }

    function description_focus() {
        last_description = $("#dataset_description").val();
    }

    function delete_dataset() {
        $.ajax({
            type: "POST",
            url: window.location.href+"/delete",
            data: {
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
            success: function() {
                window.location.href = "/";
            }
        });

    }

    function update_description() {
        var new_description = $("#dataset_description").val();

        if (last_description == new_description) {
            return;
        }
        $.ajax({
            type: "POST",
            url: window.location.href+"/patch_description",
            data: {
                "description": new_description,
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
        });

    }

    function update_sql() {
        var sql = code_mirror.getValue();

        $.ajax({
            type: "POST",
            url: window.location.href+"/patch_sql",
            data: {
                "dataset_sql": sql,
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
        });

    }


    function make_private() {
        $.ajax({
            type: "POST",
            url: window.location.href+"/toggle_public",
            data: {
                "is_public": "0",
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
            success: show_make_public
        });
    }


    function make_public() {
        $.ajax({
            type: "POST",
            url: window.location.href+"/toggle_public",
            data: {
                "is_public": "1",
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
            success: show_make_private
        });
    }

    function show_make_private() {
        $("#make_dataset_public").hide();
        $("#make_dataset_private").show();
    }

    function show_make_public() {
        $("#make_dataset_private").hide();
        $("#make_dataset_public").show();
    }

    function prep_typeahed() {
        var users = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            remote: {
                url: '/user_search/%QUERY',
                wildcard: '%QUERY'
            }
        });

        $('#user-autocomplete-container #exampleInputEmail1').typeahead(null, {
          name: 'user-list',
          display: 'login',
          source: users
        });
    }

    function add_events() {
        code_mirror = add_code_mirror();
        $("#run_query").on("click", function() { $("#update_dataset_sql").show(); });
        $("#update_dataset_sql").on("click", update_sql);
        $("#make_dataset_public").on("click", make_public);
        $("#make_dataset_private").on("click", make_private);
        $("#dataset_description").on("focus", description_focus);
        $("#dataset_description").on("blur", update_description);
        $("#delete_dataset").on("click", delete_dataset);
        // defined in run_query.js
        prep_polling_query(code_mirror);
        prep_typeahed();

    }
    return add_events;
})();
