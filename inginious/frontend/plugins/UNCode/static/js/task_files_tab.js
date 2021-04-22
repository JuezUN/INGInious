const _this = this;

function isRoot(path) {
    const rootFilenameFormat = /^\/[a-z0-9 _%\-]+\.[a-z0-9_]+$/i;
    return rootFilenameFormat.test(path);
}

jQuery(document).ready(function () {
    /**
     * Monkey-patch the studio_update_file_tabs function to know when the table is replaced with
     * the values in the table, and that way, modify the buttons.
     */
    _this.studio_update_file_tabs = (data, method) => {
        if (data == undefined)
            data = {};
        if (method == undefined)
            method = "GET";

        _getAllFiles(data, method, () => {
        });
    };

    /**
     * Patch studio_task_file_upload to detect when a file is uploaded separately, so
     * the button can be updated once the files table is rendered.
     */
    _this.studio_task_file_upload = () => {
        $('#modal_file_upload').modal('hide');
        $('#task_upload_form').ajaxSubmit({
            beforeSend: function () {
                $("#tab_file_list").html('Loading');
            },
            success: function (data) {
                $("#tab_file_list").replaceWith(data);
                modifyTabFileListButtons();
            },
            url: location.pathname + "/files"
        });
    };

    /**
     * Patch studio_task_file_delete to detect when a root file related to test is removed and remove that test too.
     * Remove test is only applied if the environment is multiLang or data science
     */
    _this.studio_task_file_delete = (path) => {
        if (!confirm("Are you sure you want to delete this?") || !studio_task_file_delete_tab(path))
            return;
        studio_update_file_tabs({"action": "delete", "path": path});
        if ((isMultiLang || isDataScience) && isRoot(path)) {
            const filename = path.substr(1);
            removeTestByFilename(filename);
        }
    };

    function _getAllFiles(data, method, callbackOnSuccess) {
        jQuery.ajax({
            beforeSend: function () {
                $("#tab_file_list").html('Loading');
            },
            success: function (data) {
                $("#tab_file_list").replaceWith(data);
                modifyTabFileListButtons();
                callbackOnSuccess();
            },
            method: method,
            data: data,
            url: location.pathname + "/files",
        });
    }

    function _addTaskFilesDeleteAllFilesButton() {
        const deleteAllFilesButton = `&nbsp;<button  type="button" class='btn btn-sm btn-danger' data-toggle='modal' 
                data-target="#delete_all_files_confirm_modal">${delete_all_files_msg}</button>`;
        $('#task_files_options_buttons').append(deleteAllFilesButton);
    }

    function _addTaskFilesUploadMultipleButton() {
        const uploadMultipleFilesButton = `<a href='#' class='btn btn-sm btn-info' data-toggle='modal' 
                data-target='#task_files_upload_multiple_modal' id='open_multiple_files_modal'>${upload_files_msg}</a>`;
        $('#task_files_options_buttons').append(uploadMultipleFilesButton);
    }

    function modifyTabFileListButtons() {
        if (!$('#open_multiple_files_modal').length) {
            const tableRows = $("#tab_file_list > table > tbody tr");
            const lastRow = tableRows[tableRows.length - 1];
            if (lastRow && lastRow.firstChild && lastRow.firstChild.nextSibling) {
                const buttons = `<div class="align-right" id="task_files_options_buttons">${lastRow.firstChild.nextSibling.innerHTML}</div><br>`;
                $("#tab_file_list > table").before(buttons);
                _addTaskFilesUploadMultipleButton();
                _addTaskFilesDeleteAllFilesButton();
                lastRow.remove();
            }
        }
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

    function closeUploadMultipleFilesModalAction() {
        // Function to describe the process to follow when the modal is closed.
        $('#task_files_upload_multiple_modal').on('hidden.bs.modal', function () {
            $("#upload_multiple_files_input").val('');
            $("#upload_multiple_files_path").val('');
            $("#list_all_files").prop("hidden", true);
        });
    }

    function taskFilesUploadMultiple() {
        $("form#upload_multiple_files_form").submit(function (e) {
            e.preventDefault();
            let error = false;
            let filesFailedUpload = [];
            let inputFiles = $("#upload_multiple_files_input").prop('files');
            let files_path = $("#upload_multiple_files_path").val();
            inputFiles = $.extend({}, inputFiles);

            $('#task_files_upload_multiple_modal').modal('hide');
            if (inputFiles.length) {
                $("#tab_file_list").html("Uploading files...");
                $.each(inputFiles, function (file_index, file) {
                    let form_data = new FormData();
                    form_data.append('action', 'upload');
                    form_data.append('path', `${files_path}/${file.name}`);
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
                            if (file_index === inputFiles.length - 1) {
                                _updateFilesTable(error, filesFailedUpload);
                            }
                        }
                    });
                });
            }
        });
    }

    function _updateFilesTable(error, filesFailedUpload) {
        studio_update_file_tabs({}, 'GET');
        let callbackOnSuccess = () => {
        };
        if (error) {
            callbackOnSuccess = () => {
                _uploadErrorAlert(filesFailedUpload)
            };
        }
        _getAllFiles({}, 'GET', callbackOnSuccess);
    }

    function _uploadErrorAlert(filesFailedUpload) {
        let tabFileList = $('#tab_file_list');
        let filesAlert = tabFileList.find("div").filter("[role=alert]");
        const message = "<p>There was an error while uploading the files: <strong>" +
            filesFailedUpload.sort().join(", ") + "</strong>. Invalid path, Maybe save the task or check that the name is not already in used. </p>";

        if (filesAlert.length) {
            filesAlert.text('');
            filesAlert.append(message)
        } else {
            const alertError = "<div class='alert alert-danger text-center' role='alert'>" + message + "</div>";
            tabFileList.prepend(alertError);
        }
    }

    function matchFilesMessage() {
        const tabFileList = $('#edit_file_tabs');
        tabFileList.prepend(`<div class="alert  alert-warning" role="alert">
        <i class="fa fa-info-circle fa-lg" aria-hidden="true"></i>
            If the uploaded files follow the format <b>'x.in'</b> and <b>'x.out'</b>, those files will be automatically
            matched as test cases (See the grader tab).
            <br>
            Additionally, files with size greater than 10MB cannot be uploaded. 
        </div>`);
    }

    function deleteAllFilesClickEvent() {
        $('#delete_all_files_btn').click(function (event) {
            event.preventDefault();
            const fileRows = $("#tab_file_list > table > tbody tr").filter((_, tableRow) => {
                return tableRow.hasAttributes() && tableRow.attributes['data-x-path'];
            });
            let errors = '';
            fileRows.each(function (_, fileRow) {
                const fileName = fileRow.attributes['data-x-path'].value;
                if (fileName === '/run') return;

                if (!studio_task_file_delete_tab(fileName)) {
                    errors += `${fileName}, `;
                }
                _deleteFile(fileName);
            });
            studio_update_file_tabs({}, 'GET');
            remove_all_test_cases();
        });
    }

    function _deleteFile(path) {
        const data = {"action": "delete", "path": path};
        jQuery.ajax({
            beforeSend: function () {
                $("#tab_file_list").html("<h4 style='color: #e99002'>Loading...</h4>");
                $("#delete_all_files_confirm_modal").modal("hide");
            },
            method: 'GET',
            async: false,
            data: data,
            url: location.pathname + "/files"
        });
    }

    modifyTabFileListButtons();
    uploadMultipleFilesOnChange();
    taskFilesUploadMultiple();
    closeUploadMultipleFilesModalAction();
    matchFilesMessage();
    deleteAllFilesClickEvent();
});
