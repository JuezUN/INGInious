jQuery(document).ready(function () {

    function addTaskFilesUploadMultipleButton() {
        $('#tab_files').mouseover(function () {
            if (!$('#open_multiple_files_modal').length) {
                let uploadFileButton = $('#edit_file_tabs_content').find('a').filter(':contains("Upload a file")');
                const uploadMultipleFilesButton = "&nbsp;<a href='#' class='btn btn-sm btn-info' data-toggle='modal' " +
                    "data-target='#task_files_upload_multiple_modal' id='open_multiple_files_modal'>Upload multiple files</a>";

                uploadFileButton.after(uploadMultipleFilesButton);
            }
        });
    }

    function uploadMultipleFilesOnChange() {
        $('#upload_multiple_files_input').change(function () {
            let inputFiles = $(this).prop('files');
            let listFilesDiv = $('#list_all_files');
            let listFiles = $.map(inputFiles, function (file) {
                return file.name;
            }).join(", ");

            if (inputFiles.length) {
                listFilesDiv.find('p[name=list_files]').text(listFiles);
                listFilesDiv.prop("hidden", false);
            } else {
                listFilesDiv.find('p[name=list_files]').text("");
                listFilesDiv.prop("hidden", true);
            }
        });
    }

    function closeModalAction() {
        // Function to describe the process to follow when the modal is closed.
        $('#task_files_upload_multiple_modal').on('hidden.bs.modal', function () {
            $("#upload_multiple_files_input").val('');
            $("#list_all_files").prop("hidden", true);
        });
    }

    function taskFilesUploadMultiple() {
        $("form#upload_multiple_files_form").submit(function (e) {
            e.preventDefault();
            let error = false;
            let filesFailedUpload = [];
            let inputFiles = $("#upload_multiple_files_input").prop('files');
            inputFiles = $.extend({}, inputFiles);
            let requestsCompleted = 0;
            let inputTestcaseFiles = [];
            let outputTestcaseFiles = [];
            $('#task_files_upload_multiple_modal').modal('hide');
            if (inputFiles.length) {
                $("#tab_file_list").html("Uploading files...");
                $.each(inputFiles, function (_, file) {                    
                    let form_data = new FormData();
                    form_data.append('action', 'upload');
                    form_data.append('path', file.name);
                    form_data.append('file', file);
                    $.ajax({
                        url: location.pathname + '/files',
                        type: 'post',
                        data: form_data,
                        contentType: false,
                        cache: false,
                        processData: false,
                        success: function (data) {
                            if (data.search(/alert/i) > 0) {
                                error = true;
                                filesFailedUpload.push(file.name);
                                
                            }
                            parts = file.name.split('.');
                            if (parts[parts.length - 1] === 'in'){
                                inputTestcaseFiles.push(file.name)
                            } else if (parts[parts.length - 1] === 'out'){
                                outputTestcaseFiles.push(file.name);
                            }
                            requestsCompleted++;
                            if (requestsCompleted === inputFiles.length) {
                                callbackLastUploadedFile(error, data, filesFailedUpload);
                                matchTestCases(inputTestcaseFiles, outputTestcaseFiles);
                            }
                        }
                    });
                });
            }
        });
    }

    function callbackLastUploadedFile(error, resultData, filesFailedUpload) {
        $("#tab_file_list").replaceWith(resultData);
        if (error) {
            uploadErrorAlert(filesFailedUpload);
        }
    }

    function uploadErrorAlert(filesFailedUpload) {
        let tabFileList = $('#tab_file_list');
        let filesAlert = tabFileList.find("div").filter("[role=alert]");
        const message = "<p>There was an error while uploading the files: <strong>" +
            filesFailedUpload.sort().join(", ") + "</strong>. They may be already uploaded.</p>";

        if (filesAlert.length) {
            filesAlert.text('');
            filesAlert.append(message)
        } else {
            const alertError = "<div class='alert alert-danger text-center' role='alert'>" + message + "</div>";
            tabFileList.prepend(alertError);
        }
    }

    function matchTestCases(inputFiles, outputFiles){
        for(it in inputFiles){        
            parts = inputFiles[it].split('.');        
            name = parts.splice(0, parts.length - 1).join(".");
            if (outputFiles.includes(name + '.out')){
                test_case = {
                    'input_file': inputFiles[it],
                    'output_file': name + '.out'
                };
                studio_add_test_case(test_case);
            }
        }
    
    }

    addTaskFilesUploadMultipleButton();
    uploadMultipleFilesOnChange();
    taskFilesUploadMultiple();
    closeModalAction();

});

