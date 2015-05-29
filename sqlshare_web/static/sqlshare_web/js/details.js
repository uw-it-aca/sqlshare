var prep_details_page = (function() {
    "use strict";

    function add_code_mirror() {
        var el = document.getElementById("dataset_sql");

        // work around jshint - newcap error.
        var func_code_mirror = CodeMirror;
        var codemirror = func_code_mirror(function(cm) {
            el.parentNode.replaceChild(cm, el);
        }, {
            textWrapping: false,
            autoMatchParens: true,
            mode:  "text/x-mssql",
            lineNumbers: true,
            smartIndent: true,
            extraKeys: {
                Tab: false
            },
            value: el.innerHTML
        });

        return codemirror;
    }


    function add_events() {
        var code_mirror = add_code_mirror();
        // defined in run_query.js
        prep_polling_query(code_mirror);

    }
    return add_events;
})();
