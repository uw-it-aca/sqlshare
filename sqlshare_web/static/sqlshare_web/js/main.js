function create_uploader() {
    "use strict";
    var r = new Resumable({
        target:'/upload_chunk/',
        simultaneousUploads: 1,
        chunkSize: 1,
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
        $("#chunk_upload_container").hide();
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
}


function add_finalize_form_events() {
    "use strict";
    // Chunk one is uploaded for the dataset preview.
    var current_file_chunk = 2;

    function has_title() {
        if ($("#id_dataset_name").val().match(/[a-zA-Z0-9]/))   {
            return true;
        }
        return false;
    }

    function post_chunk_upload(data, text_status) {
        console.log(data, text_status);
        if (data == "next_chunk") {
            current_file_chunk += 1;
            upload_next_chunk();
            return;
        }
        if (data == "upload_complete") {
            send_finalize();
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
                "is_public": $("input[name='is_public']").is(':checked')
            },
            success: post_chunk_upload
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
            $("#save_button").prop("disabled", false);
        }
        else {
            $("#title_required").show();
            $("#save_button").prop("disabled", true);
        }
    });


    $("#save_button").click(function() {
        if (has_title()) {
            $("#final_settings_panel").hide();
            $("#uploading_panel").show();
            upload_next_chunk();
        }
    });
}

