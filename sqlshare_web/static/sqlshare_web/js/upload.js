function create_uploader() {
    "use strict";
    var r = new Resumable({
        target:'/upload_chunk/',
        simultaneousUploads: 1,
        //chunkSize: 1,
        maxFiles: 1,
        query: {
            'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
        }
    });


    if (!r.support) {
        $("#chunk_upload_container").hide();
        $("#old_school_panel").show();
        return;
    }

    r.on('fileAdded', function() { r.upload(); });
    r.on('uploadStart', function(){
        //$("#chunk_upload_container").hide();
        $("#uploading_panel").show();
    });
    r.on('complete', function(){
        window.location.href = "/upload/parser/"+r.files[0].fileName;
    });
    r.on('progress', function(){
        $("#progress_meter").css("width", (100 * r.progress())+"%");
        $("#progress_meter").html(Math.round(100 * r.progress())+"%");
        $("#progress_meter").attr("aria-valuenow", Math.round(100 * r.progress()));
    });

    r.assignBrowse(document.getElementById('upload_dataset_browse'));
    r.assignDrop(document.getElementById('upload_dataset_droptarget'));

}

function add_parser_form_events() {
    "use strict";
    var PERCENTAGE_OF_FINALIZE_IN_UPLOAD = 10;

    function update_preview() {
        $("#update_preview").val("1");
        $("#dataset_parser_form").submit();
    }

    $("#dataset_delimiter").change(function() {
        update_preview();
    });

    $("#has_column_headers").change(function() {
        update_preview();
    });

    // Chunk one is uploaded for the dataset preview.
    var current_file_chunk = 2;

    function has_title() {
        if ($("#id_dataset_name").val().match(/[a-zA-Z0-9]/) && !has_invalid_title())   {
            return true;
        }
        return false;
    }

    function has_invalid_title() {
        if ($("#id_dataset_name").val().match(/[\[\]/\\\?#]/)) {
            return true;
        }
        return false;
    }

    function post_chunk_upload(data, text_status) {
        if (data.state == "next_chunk") {
            var finished = data.finished;
            var max = data.max;

            if (max) {
                var base = finished / max;
                var percent_to_fill = (PERCENTAGE_OF_FINALIZE_IN_UPLOAD / 100);
                var scaled = base * percent_to_fill;
                var total = 100 * scaled;

                $("#finalizing_progress").css("width", total+"%");
                $("#finalizing_progress").html(Math.round(total)+"%");
                $("#finalizing_progress").attr("aria-valuenow", Math.round(total));
            }


            current_file_chunk += 1;
            upload_next_chunk();
            return;
        }
        if (data == "upload_complete") {
            send_finalize();
        }
    }

    function send_to_dataset(data, text_status, xhr) {
        window.location.href = xhr.getResponseHeader("Location");
    }

    function poll_finalize(data, text_status, xhr) {
        var filename = $("input[name='original_name']").val();
        var dataset_name = $("#id_dataset_name").val();
        if (data.state == "Done") {
            window.location.href = "/detail/"+encodeURIComponent(sqlshare_user)+"/"+encodeURIComponent(dataset_name);
        }
        else {
            var rows_total = data.rows_total,
                rows_loaded = data.rows_loaded;

            if (rows_total) {
                // Finalizing is the last half - so we start at 50% here,
                // then take half of this percentage...
                var base = rows_loaded / rows_total;
                var percent_to_fill = 1 - (PERCENTAGE_OF_FINALIZE_IN_UPLOAD / 100);
                var scaled = base * percent_to_fill;
                var total = 100 * (1 - percent_to_fill + scaled);

                $("#finalizing_progress").css("width", total+"%");
                $("#finalizing_progress").html(Math.round(total)+"%");
                $("#finalizing_progress").attr("aria-valuenow", Math.round(total));
            }
            window.setTimeout(function() {
                $.ajax({
                    url: "/upload/finalize_process/" + filename,
                    method: "GET",
                    success: poll_finalize,
                });
            }, 1000);

        }
    }

    function send_finalize() {
        var filename = $("input[name='original_name']").val();
        $.ajax({
            url: "/upload/finalize_process/" + filename,
            method: "POST",
            data: {
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val(),
                "finalize": true,
                "dataset_name": $("input[name='dataset_name']").val(),
                "dataset_description": $("textarea[name='dataset_description']").val(),
                "is_public": $("input[name='is_public']").is(':checked') ? "public" : "private"
            },
            success: poll_finalize
        });

    }

    function upload_next_chunk() {
        var filename = $("input[name='original_name']").val();
        $.ajax({
            url: "/upload/finalize_process/" + filename,
            method: "POST",
            data: {
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val(),
                chunk: current_file_chunk
            },
            success: post_chunk_upload
        });
    }

    $("#id_dataset_name").keyup(function() {
        if (has_title()) {
            $("#title_required").hide();
            $("#invalid_title").hide();
            $("#save_button").prop("disabled", false);
        }
        else {
            if (has_invalid_title()) {
                $("#invalid_title").show();
                $("#title_required").hide();
            }
            else {
                $("#title_required").show();
                $("#invalid_title").hide();
            }
            $("#save_button").prop("disabled", true);
        }
    });


    $("#save_button").click(function() {
        if (has_title()) {
            $("#dataset_parser_settings_panel").hide();
            $("#final_settings_panel").hide();
            $("#dataset_preview_panel").hide();
            $("#uploading_panel").show();
            upload_next_chunk();
        }

        return false;
    });
}

function add_datasetlist_events() {
    $("#dataset_list_scroll").jscroll({
        loadingHtml: '<div style="line-height:80px; text-align:center;" class="text-muted"><i class="fa fa-spinner fa-spin"></i> Loading...</div>',
    });
    $("#dataset_search_input").on("keydown", function() {
        $("#clear_dataset_search_button").hide();
        $("#run_dataset_search_button").show();
    });
}

