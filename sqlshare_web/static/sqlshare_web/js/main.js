function create_uploader() {
    "use strict";
    var r = new Resumable({
        target:'/upload_chunk/',
        simultaneousUploads: 1,
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
    });

    r.assignBrowse(document.getElementById('upload_dataset_browse'));
    r.assignDrop(document.getElementById('upload_dataset_droptarget'));

}
