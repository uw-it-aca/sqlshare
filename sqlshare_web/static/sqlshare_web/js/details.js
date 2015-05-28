var prep_details_page = function() {
    "use strict";

    function add_code_mirror() {
        var el = document.getElementById("dataset_sql");

        var codemirror = CodeMirror(function(cm) {
            el.parentNode.replaceChild(cm, el);
        }, {
            textWrapping: false,
            mode:  "text/x-mssql",
            lineNumbers: true,
            value: el.innerHTML
        });
    }

    add_code_mirror();
};
