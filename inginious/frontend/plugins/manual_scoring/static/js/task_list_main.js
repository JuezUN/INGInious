const DOWNLOAD_CSV_BTN_ID = "download_csv";
const RESULT_INFO_AREA_ID = "information_area";

function getManualScoringInfo(course_id) {
    const contentDanger = "Error getting the information. Try later";
    return $.get(`/api/manual_scoring/${course_id}`, function (result) {
        exportCSVFile(result, "test");
    }, "json").fail(function () {
        new MessageBox(RESULT_INFO_AREA_ID, contentDanger, "danger", false);
    });
}

function exportCSVFile(items, fileTitle) {
    const filename = `${fileTitle}.csv`;
    const csv = 'data:text/csv;charset=utf-8,' + Papa.unparse(items);
    const data = encodeURI(csv);
    const link = document.createElement('a');

    link.setAttribute('href', data);
    link.setAttribute('download', filename);

    // Append link to the body in order to make it work on Firefox.
    document.body.appendChild(link);

    link.click();
    link.remove();
}

function addListenerToDownloadButton() {
    const course = getCourseId();
    $(`#${DOWNLOAD_CSV_BTN_ID}`).click(function () {
        getManualScoringInfo(course);
    });
}

function displaySaveRubricAlertError(data) {
    const alertElement = $("#save_rubric_alert");
    alertElement.prop("class", "alert alert-danger");
    if (typeof data !== "string") {
        alertElement.text("Something went wrong while saving the rubric. Please try again.");
    } else {
        alertElement.text(data);
    }
    alertElement.prop("hidden", false);
}

function displaySaveRubricAlertSuccess(data) {
    const alertElement = $("#save_rubric_alert");
    alertElement.prop("class", "alert alert-success");
    alertElement.text(data);
    alertElement.prop("hidden", false);
}

function preventModalToBeClosed() {
    $("#upload_custom_rubric_modal").modal({backdrop: "static", keyboard: false});
    $("#upload_custom_rubric_modal button[data-dismiss=modal]").each(function () {
        $(this).prop("disabled", true);
    });
}

function makeModalClosable() {
    $("#upload_custom_rubric_modal").modal({backdrop: '', keyboard: true});
    $("#upload_custom_rubric_modal button[data-dismiss=modal]").each(function () {
        $(this).prop("disabled", false);
    });
}

function onSubmitSaveRubric() {
    $("form#upload_rubric_file").submit(function (e) {
        e.preventDefault();
        const file = $("#rubric_file").prop("files")[0];
        const allowedFileExtensions = /(\.json)$/i;
        if (file === undefined) {
            displaySaveRubricAlertError("Please select a file before submitting it.");
        } else if (!allowedFileExtensions.exec(file.name)) {
            displaySaveRubricAlertError("The inserted file should be a .json file.");
        } else {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("course", getCourseId());
            $.ajax({
                url: "/api/manual_scoring/upload_custom_rubric",
                method: "POST",
                dataType: "json",
                data: formData,
                mimeType: "multipart/form-data",
                processData: false,
                contentType: false,
                beforeSend: function () {
                    $("#submit_save_rubric").prop("disabled", true);
                    preventModalToBeClosed();
                },
                success: function (data) {
                    makeModalClosable();
                    if (data["status"] === "error") {
                        displaySaveRubricAlertError(data["text"]);
                    } else {
                        displaySaveRubricAlertSuccess(data["text"]);
                    }
                    $("#submit_save_rubric").prop("disabled", false);
                },
                error: function (data) {
                    displaySaveRubricAlertError(data["text"]);
                    makeModalClosable();
                    $("#submit_save_rubric").prop("disabled", false);
                }
            });
        }
    });
}

function closeModalEvent() {
    // Function to describe the process to follow when the modal is closed.
    $("#upload_custom_rubric_modal").on("hidden.bs.modal", function () {
        $("#rubric_file").val('');
        $("#save_rubric_alert").prop("hidden", true);
    });
}

function setupDownloadRubric() {
    const filename = "default_rubric.json";
    const data = encodeURI("data:text/json;charset=utf-8," + getRubric());
    const anchorElement = $("#download_rubric");

    anchorElement.attr("href", data);
    anchorElement.attr("download", filename);
}

jQuery(document).ready(function () {
    addListenerToDownloadButton();
    onSubmitSaveRubric();
    closeModalEvent();
    setupDownloadRubric();
});
