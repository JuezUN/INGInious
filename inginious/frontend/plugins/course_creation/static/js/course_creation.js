function displayCourseCreationAlertError(data) {
    const alertElement = $("#create_course_alert");
    alertElement.prop("class", "alert alert-danger");
    alertElement.html("");
    if (!("text" in data)) {
        alertElement.html("Something went wrong while creating the course. Please try again.");
    } else {
        alertElement.html(data["text"]);
    }
    alertElement.prop("hidden", false);
}

function displayCourseCreationSuccessAlert(data) {
    const alertElement = $("#create_course_alert");
    alertElement.prop("class", "alert alert-success");
    alertElement.html(data["text"]);
    alertElement.prop("hidden", false);
}

function displayCourseCreationLoadingAlert() {
    const alertElement = $("#create_course_alert");
    alertElement.prop("class", "alert alert-info");
    const spinner = "<i class='fa fa-spinner fa-pulse fa-fw' aria-hidden='true'></i>";
    alertElement.html(spinner + " The course is being created...");
    alertElement.prop("hidden", false);
}

function preventCourseCreationModalToBeClosed() {
    $("#create_course_modal").modal({backdrop: "static", keyboard: false});
    $("#create_course_modal button[data-dismiss=modal]").each(function () {
        $(this).prop("disabled", true);
    });
}

function makeCourseCreationModalClosable() {
    $("#create_course_modal").modal({backdrop: "", keyboard: true});
    $("#create_course_modal button[data-dismiss=modal]").each(function () {
        $(this).prop("disabled", false);
    });
}

function blurCourseCreationModal() {
    $("#create_course_modal input").prop("disabled", true);
    $("#list_copy_courses").prop("disabled", true);
    $("#submit_create_course").prop("disabled", true);
}

function unblurCourseCreationModal() {
    $("#create_course_modal input").prop("disabled", false);
    $("#list_copy_courses").prop("disabled", false);
    $("#submit_create_course").prop("disabled", false);
}

function redirectToCoursePage(data) {
    const win = window.open(location.origin + data["course_page"]);
    win.focus();
}

function onSubmitCourseCreation() {
    const data = {
        "course_name": $("#course_name").val(),
        "course_group": $("#course_group").val(),
        "course_year": $("#course_year").val(),
        "course_period": $("#course_period").val(),
        "course_to_copy_id": $("#list_copy_courses").val(),
    };
    $.ajax({
        url: "/api/create_course",
        method: "POST",
        dataType: "json",
        data,
        beforeSend: () => {
            blurCourseCreationModal();
            preventCourseCreationModalToBeClosed();
            displayCourseCreationLoadingAlert();
        },
        success: (data) => {
            unblurCourseCreationModal();
            makeCourseCreationModalClosable();
            displayCourseCreationSuccessAlert(data);
            redirectToCoursePage(data);
        },
        error: (data) => {
            const response = data.responseJSON || {};
            makeCourseCreationModalClosable();
            unblurCourseCreationModal();
            displayCourseCreationAlertError(response);
        }
    });
}

function onCloseModal() {
    // Function to restart the form when the modal is closed.
    $("#create_course_modal").on("hidden.bs.modal", function () {
        $("#create_course_modal input").val("");
        $("#list_copy_courses").val("-1");
        $("#create_course_alert").prop("hidden", true);
    });
}

jQuery(document).ready(function () {
    onCloseModal();
    $("#create_course_form").submit(function (e) {
        e.preventDefault();
    });

    $("#course_year").val(new Date().getFullYear());
    $("#course_year").datetimepicker();
});