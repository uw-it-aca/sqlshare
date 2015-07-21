var prep_details_page = (function() {
    "use strict";
    var last_description,
        code_mirror,
        user_template;

    user_template = Handlebars.compile($("#user-access-item").text());

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

    function show_update_message() {
        $("#update_dataset_message").fadeIn();

        window.setTimeout(function() {
            $("#update_dataset_message").fadeOut();
        }, 2000);
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
            success: show_update_message,
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

    function addUserOnEnter(ev) {
        if (ev.keyCode === 13) {
            addUserFromInput();
        }
    }

    function addUserFromInput() {
        var username = $("#exampleInputEmail1").val();
        username = username.replace(/^ +/, "").replace(/ +$/, "");

        if (username) {
            var content = user_template({ username: username });
            $("#dataset_access_list").append($(content));
        }
        $('#user-autocomplete-container #exampleInputEmail1').typeahead('close');
        $('#user-autocomplete-container #exampleInputEmail1').typeahead('val', "");
        $("#exampleInputEmail1").val("");
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


        $("#exampleInputEmail1").on("keypress", addUserOnEnter);
    }

    function save_permissions() {
        addUserFromInput();
        window.setTimeout(function() {
            var checked = $("input[name='dataset_account']:checked");
            var len = checked.length;

            var accounts = [];
            for (var i = 0; i < len; i++) {
                accounts.push(checked[i].value);
            }

            $.ajax({
                type: "POST",
                url: window.location.href+"/permissions",
                data: {
                    "accounts": accounts,
                    'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
                },
                success: hide_sharing_panel
            });
        }, 0);
    }

    function hide_sharing_panel() {
        $("#share_modal").modal('hide');
    }

    function show_permissions_panel(data) {
        $("#dataset_access_list").html("");
        for (var i = 0; i < data.length; i++) {
            var content = user_template({ username: data[i] });
            $("#dataset_access_list").append($(content));
        }
        $("#sharing-modal-loading").hide();
        $("#sharing-modal-display").show();
    }

    function load_permissions_data() {
        $("#sharing-modal-display").hide();
        $("#sharing-modal-loading").show();
        $.ajax({
            type: "GET",
            url: window.location.href+"/permissions",
            success: show_permissions_panel
        });
    }

    function create_new_dataset_from_query() {
        $("#new_query_sql").val(code_mirror.getValue());
        $("#new_dataset_from_query_form").submit();
    }

    function create_new_dataset_derive() {
        $("#new_dataset_by_derive_form").submit();
    }

    function add_events(preview_query_id) {
        // defined in run_query.js
        code_mirror = prep_polling_query(null, preview_query_id);
        $("#run_query").on("click", function() { $("#update_dataset_sql").show(); });
        $("#update_dataset_sql").on("click", update_sql);
        $("#make_dataset_public").on("click", make_public);
        $("#make_dataset_private").on("click", make_private);
        $("#dataset_description").on("focus", description_focus);
        $("#dataset_description").on("blur", update_description);
        $("#delete_dataset").on("click", delete_dataset);
        $("#save_permissions_button").on("click", save_permissions);
        $("#new_dataset_from_query").on("click", create_new_dataset_from_query);
        $("#new_dataset_derive").on("click", create_new_dataset_derive);
        prep_typeahed();
        $("#share_modal").on('show.bs.modal', load_permissions_data);

        return code_mirror;

    }
    return add_events;
})();
