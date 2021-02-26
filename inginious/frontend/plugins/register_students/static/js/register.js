jQuery(document).ready(function () {

    let registerSucceeded = false;

    function displayRegisterStudentsAlertError(data) {
        const alertElement = $("#register_students_alert");
        alertElement.prop("class", "alert alert-danger");
        if (typeof data !== "string") {
            alertElement.text("Something went wrong while registering the students. Please try again.");
        } else {
            alertElement.text(data);
        }
        alertElement.prop("hidden", false);
    }

    function displayLoadingAlert() {
        const alertElement = $("#register_students_alert");
        alertElement.prop("class", "alert alert-info");
        alertElement.text("Registering students...");
        alertElement.prop("hidden", false);
    }

    function preventModalToBeClosed() {
        $("#register_students_modal").modal({backdrop: "static", keyboard: false});
        $("#register_students_modal button[data-dismiss=modal]").each(function () {
            $(this).prop("disabled", true);
        });
    }

    function makeModalClosable() {
        $("#register_students_modal").modal({backdrop: '', keyboard: true});
        $("#register_students_modal button[data-dismiss=modal]").each(function () {
            $(this).prop("disabled", false);
        });
    }

    function runRegisterStudents(data) {
        // Function executed when the Ajax request success.
        if ("status" in data && data["status"] === "error") {
            displayRegisterStudentsAlertError(data["text"]);
        } else if ("status" in data && data["status"] === "success") {
            const alertElement = $("#register_students_alert");
            registerSucceeded = true;
            $("#students_file").val('');
            alertElement.prop("class", "alert alert-warning");
            alertElement.text("");
            alertElement.append($.parseHTML(data["text"]));
            alertElement.prop("hidden", false);
            setTimeout(function () {
                alertElement.prop("hidden", true);
            }, 100000);
        } else {
            displayRegisterStudentsAlertError("An error occurred while registering. Please try again.");
        }
    }

    function getCourseId() {
        return window.location.href.split("/")[4]; // Get the course id using the current URL.
    }

    function submitRegisterStudents() {
        $("form#upload_students_file").submit(function (e) {
            e.preventDefault();
            const file = $("#students_file").prop("files")[0];
            const language = $("#email_language").val();
            const allowedFileExtensions = /(\.csv)$/i;
            if (file === undefined) {
                displayRegisterStudentsAlertError("Please select a file before submitting it.");
            } else if (!allowedFileExtensions.exec(file.name)) {
                displayRegisterStudentsAlertError("The inserted file should be a .csv file.");
            } else {
                const formData = new FormData();
                formData.append("file", file);
                formData.append("course", getCourseId());
                formData.append("language", language);
                $.ajax({
                    url: "/api/addStudents/",
                    method: "POST",
                    dataType: "json",
                    data: formData,
                    mimeType: "multipart/form-data",
                    processData: false,
                    contentType: false,
                    beforeSend: function () {
                        $("#submit_register_students").prop("disabled", true);
                        preventModalToBeClosed();
                        displayLoadingAlert();
                    },
                    success: function (data) {
                        runRegisterStudents(data);
                        makeModalClosable();
                        $("#submit_register_students").prop("disabled", false);
                    },
                    error: function (data) {
                        displayRegisterStudentsAlertError(data);
                        makeModalClosable();
                        $("#submit_register_students").prop("disabled", false);
                    }
                });
            }
        });
    }

    function appendRegisterStudentsButton() {
        // Function intended for appending the button to open the modal in the 'students' page.
        const html = "<br><button class='btn btn-success' data-toggle='modal' data-target='#register_students_modal'>" +
            "<i class='fa fa-users'></i> Register students</button>";
        const tabStudents = $("#tab_students");
        tabStudents.append(html);
    }

    function closeModal() {
        // Function to describe the process to follow when the modal is closed.
        $("#register_students_modal").on("hidden.bs.modal", function () {
            if (registerSucceeded) {
                window.location.replace(window.location.href);
            } else {
                $("#students_file").val('');
                $("#register_students_alert").prop("hidden", true);
            }
        });
    }

    closeModal();
    appendRegisterStudentsButton();
    submitRegisterStudents();
});
