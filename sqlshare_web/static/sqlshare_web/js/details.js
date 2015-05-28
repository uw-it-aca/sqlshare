var prep_details_page = function() {
    "use strict";

    function add_code_mirror() {
        var el = document.getElementById("dataset_sql");

        // work around jshint - newcap error.
        var func_code_mirror = CodeMirror;
        var codemirror = func_code_mirror(function(cm) {
            el.parentNode.replaceChild(cm, el);
        }, {
            textWrapping: false,
            mode:  "text/x-mssql",
            lineNumbers: true,
            readOnly: true,
            value: el.innerHTML
        });
    }

    add_code_mirror();
};
