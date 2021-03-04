function displayCourseCreationAlertError(data) {
    const alertElement = $("#create_course_alert");
    alertElement.prop("class", "alert alert-danger");
    if (!("text" in data)) {
        alertElement.text("Something went wrong while creating the course. Please try again.");
    } else {
        alertElement.text(data["text"]);
    }
    alertElement.prop("hidden", false);
}

function preventModalToBeClosed() {
    $("#create_course_modal").modal({backdrop: "static", keyboard: false});
    $("#create_course_modal button[data-dismiss=modal]").each(function () {
        $(this).prop("disabled", true);
    });
}

function makeModalClosable() {
    $("#create_course_modal").modal({backdrop: '', keyboard: true});
    $("#create_course_modal button[data-dismiss=modal]").each(function () {
        $(this).prop("disabled", false);
    });
}

function redirectToCoursePage(data) {
    location.href = location.origin + data["course_page"]
}

function onSubmitCourseCreation() {
    $("form#create_course_form").submit(function (e) {
        e.preventDefault();
        const data = {
            "course_name": $("#course_name").val(),
            "course_group": $("#course_group").val(),
            "course_year": $("#course_year").val(),
            "course_semester": $("#course_semester").val(),
        };
        $.ajax({
            url: "/api/create_course",
            method: "POST",
            dataType: "json",
            data: data,
            beforeSend: function () {
                $("#submit_create_course").prop("disabled", true);
                preventModalToBeClosed();
            },
            success: function (data) {
                redirectToCoursePage(data);
                makeModalClosable();
                $("#submit_create_course").prop("disabled", false);
            },
            error: function (data) {
                const response = data.responseJSON || {};
                displayCourseCreationAlertError(response);
                makeModalClosable();
                $("#submit_create_course").prop("disabled", false);
            }
        });
    });
}

jQuery(document).ready(function () {
    onSubmitCourseCreation();
});