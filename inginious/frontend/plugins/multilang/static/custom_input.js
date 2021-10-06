function getTaskIdFromUrl() {
    let urlTokens = window.location.pathname.split("/");
    return urlTokens[urlTokens.length - 1];
}

function getCourseIdFromUrl() {
    let urlTokens = window.location.pathname.split("/");
    return urlTokens[urlTokens.length - 2];
}

function displayCustomTestAlertError(content) {
    displayTaskStudentAlertWithProblems(content, "danger");
}

function displayTimeOutAlert(content) {
    displayTaskStudentAlertWithProblems(content, "warning");
}

function displayOverflowAlert(content) {
    displayTaskStudentAlertWithProblems(content, "danger");
}

function displaySuccessAlert(content) {
    displayTaskStudentAlertWithProblems(content, "success");
}

function displayCustomInputResults(data, customTestOutputArea = null, placeholderSpan = null) {
    if ("status" in data && data["status"] === "done") {
        if ("result" in data) {
            const result = data["result"];
            if (customTestOutputArea) {
                const stdoutSpan = $("<span/>").addClass("stdout-text").text(data.stdout);
                const stderrSpan = $("<span/>").addClass("stderr-text").text(data.stderr);
                customTestOutputArea.append(stdoutSpan);
                customTestOutputArea.append(stderrSpan);
            }

            if (result === "failed") {
                displayCustomTestAlertError(data);
            } else if (result === "timeout") {
                displayTimeOutAlert(data);
            } else if (result === "overflow") {
                displayOverflowAlert(data);
            } else if (result === "success") {
                displaySuccessAlert(data);
            } else {
                displayCustomTestAlertError(data);
            }
        }
    } else if ("status" in data && data["status"] === "error") {
        if (customTestOutputArea) {
            customTestOutputArea.html(placeholderSpan);
        }
        if (data["result"] === "timeout") {
            data["text"] = "Your submission timed out.";
            displayTimeOutAlert(data);
        } else {
            displayCustomTestAlertError(data);
        }
    } else {
        if (customTestOutputArea) {
            customTestOutputArea.html(placeholderSpan);
        }
        displayCustomTestAlertError({});
    }
}

function waitForCustomTest(customTestId) {
    setTimeout(() => {
        let url = "/api/custom_input_notebook/";
        /* If task is lti, set the session id from task page in api url of the plugin.
           All api calls in task view that requieres the user's session must add this validation.
        */
        if(is_lti()){
            url = "/" + ($("form#task").attr("action").split("/")[1]) + url;
        }
        $.get(url, {"custom_test_id": customTestId})
            .done((data) => {
                data = JSON.parse(data);
                if ("status" in data && data["status"] === "waiting") {
                    displayTaskLoadingAlert(data, null);
                    waitForCustomTest(customTestId);
                } else if ("status" in data && data["status"] === "done") {
                    displayCustomInputResults(data);
                    unblurTaskForm();
                } else {
                    displayCustomTestAlertError(data);
                    unblurTaskForm();
                }
            })
            .fail((data) => {
                const response = JSON.parse(data.responseJSON || "{}");
                if ("status" in response && response["status"] === "error" && "text" in response) {
                    displayCustomTestAlertError(response);
                } else {
                    displayCustomTestAlertError({
                        "text": "An error occurred while running the custom tests. Please try again or submitting " +
                            "to know the results."
                    });
                }
                unblurTaskForm();
            });
    }, 1000);
}

function apiTestNotebookRequest(inputId, taskForm) {
    // POST REQUEST to run custom tests for Notebooks.
    if (!taskFormValid()) return;

    $("html, body").animate({
        scrollTop: $("#task_alert").offset().top - 100
    }, 200);
    blurTaskForm();
    sendTestNotebookAnalytics();

    let url = "/api/custom_input_notebook/";

    /* If task is lti, set the session id from task page in api url of the plugin.
       All api calls in task view that requieres the user's session must add this validation.
    */
    if(is_lti()){
        url = "/" + ($("form#task").attr("action").split("/")[1]) + url
    }

    $.ajax({
        url: url,
        method: "POST",
        dataType: "json",
        data: taskForm,
        processData: false,
        contentType: false,
        success: (data) => {
            data = JSON.parse(data);
            if ("status" in data && data["status"] === "error") {
                displayCustomTestAlertError(data);
                unblurTaskForm();
            } else {
                displayTaskLoadingAlert(data, null);
                waitForCustomTest(data["custom_test_id"]);
            }
        },
        error: (data) => {
            const response = JSON.parse(data.responseJSON || "{}");
            if ("status" in response && response["status"] === "error" && "text" in response) {
                displayCustomTestAlertError(response);
            } else {
                displayCustomTestAlertError({
                    "text": "An error occurred while running the custom tests. The tests likely took more time " +
                        "than expect or check your session has not expired. Please try again or try submitting to " +
                        "know the results."
                });
            }
            unblurTaskForm();
        }
    });
}

function apiCustomInputRequest(inputId, taskform) {
    // POST REQUEST for running code with custom input
    const customTestOutputArea = $("#customoutput-" + inputId);
    const placeholderSpan = "<span class='placeholder-text'>Your output goes here</span>";
    if (!taskFormValid()) return;

    let url = "/api/custom_input/";

    /* If task is lti, set the session id from task page in api url of the plugin.
       All api calls in task view that requieres the user's session must add this validation.
    */
    if(is_lti()){
        url = "/" + ($("form#task").attr("action").split("/")[1]) + url
    }

    const runCustomInputCallback = function (data) {
        data = JSON.parse(data);
        customTestOutputArea.empty();
        displayCustomInputResults(data, customTestOutputArea, placeholderSpan);
        unblurTaskForm();
    };

    blurTaskForm();
    resetAlerts();
    customTestOutputArea.html("Running...");

    sendCustomInputAnalytics();

    $.ajax({
        url: url,
        method: "POST",
        dataType: "json",
        data: taskform,
        processData: false,
        contentType: false,
        success: runCustomInputCallback,
        error: function (error) {
            unblurTaskForm();
            customTestOutputArea.html(placeholderSpan);
        }
    });
}

function runCustomTest(inputId, environment = "multilang") {
    /**
     * Identifies current page and search task identifier
     * and course identifier (GET Request to API) for running
     * the student code with custom input.
     */
    const taskForm = new FormData($("form#task")[0]);
    taskForm.set("submit_action", "customtest");
    taskForm.set("courseid", getCourseId());
    taskForm.set("taskid", getTaskId());

    if (environment === "multilang") {
        apiCustomInputRequest(inputId, taskForm);
    } else if (environment === "Notebook") {
        taskForm.set(`${inputId}/input`, taskForm.getAll(`${inputId}/custom_tests`));
        apiTestNotebookRequest(inputId, taskForm);
    }
}

function sendCustomInputAnalytics() {
    let url = "/api/analytics/";
    //Verify if is a lti task, and set the actual session id from task page (Do that for all analytics calls in task view)
    if(is_lti()){
        url = "/" + ($("form#task").attr("action").split("/")[1]) + url; 
    }
    $.post(url, {
        service: {
            key: "custom_input",
            name: "Custom input"
        },
        course_id: getCourseId(),
    });
}

function sendTestNotebookAnalytics() {
    let url = "/api/analytics/";
    //Verify if is a lti task, and set the actual session id from task page (Do that for all analytics calls in task view)
    if(is_lti()){
        url = "/" + ($("form#task").attr("action").split("/")[1]) + url; 
    }
    $.post(url, {
        service: {
            key: "custom_input_notebook",
            name: "Custom input notebook"
        },
        course_id: getCourseId(),
    });
}


$(document).ready(function () {
    let lastValidSelection = null;
    $("#select_test").change(function (event) {
        if ($(this).val().length > 3) {
            $(this).val(lastValidSelection);
        } else {
            lastValidSelection = $(this).val();
        }
    });
});