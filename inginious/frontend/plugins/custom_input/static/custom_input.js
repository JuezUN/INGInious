function getTaskIdFromUrl() {
    let urlTokens = window.location.pathname.split("/");
    return urlTokens[urlTokens.length - 1];
}

function getCourseIdFromUrl() {
    let urlTokens = window.location.pathname.split("/");
    return urlTokens[urlTokens.length - 2];
}

function getCurrentPageName() {
    let urlTokens = window.location.pathname.split("/");
    return urlTokens[1];

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

function apiCustomInputRequest(inputId, taskform){
    // POST REQUEST for running code with custom input
    let customTestOutputArea = $('#customoutput-'+inputId);
    let placeholderSpan = "<span class='placeholder-text'>Your output goes here</span>";

    let runCustomTestCallBack = function (data) {
        data = JSON.parse(data);
        customTestOutputArea.empty();

        if ('status' in data && data['status'] == 'done') {
            if ('result' in data) {
                let result = data['result'];
                let stdoutSpan = $("<span/>").addClass("stdout-text").text(data.stdout);
                let stderrSpan = $("<span/>").addClass("stderr-text").text(data.stderr);
                customTestOutputArea.append(stdoutSpan);
                customTestOutputArea.append(stderrSpan);

                if (result == 'failed') {
                    displayCustomTestAlertError(data);
                } else if (result == "timeout") {
                    displayTimeOutAlert(data);
                } else if (result == "overflow") {
                    displayOverflowAlert(data);
                } else if (result != "success") {
                    displayCustomTestAlertError(data);
                }
            }
        } else if ('status' in data && data['status'] == 'error') {
            customTestOutputArea.html(placeholderSpan);
            if (data["result"] == "timeout") {
                data["text"] = "Your code did not finished. Your code TIMED OUT.";
                displayTimeOutAlert(data);
            } else {
                displayCustomTestAlertError(data);
            }
        } else {
            customTestOutputArea.html(placeholderSpan);
            displayCustomTestAlertError({});
        }

        unblurTaskForm();
    };

    blurTaskForm();
    resetAlerts();
    customTestOutputArea.html("Running...");

    $.ajax({
            url: '/api/custom_input/',
            method: "POST",
            dataType: 'json',
            data: taskform,
            processData: false,
            contentType: false,
            success: runCustomTestCallBack,
            error: function (error) {
                unblurTaskForm();
                customTestOutputArea.html(placeholderSpan);
            }
    });
}

function runCustomTest (inputId) {
    /**
     * Identifies current page and search task identifier
     * and course identifier (GET Request to API) for running
     * the student code with custom input.
     */
    let taskForm = new FormData($('form#task')[0]);
    taskForm.set("submit_action", "customtest");

    if('course' === getCurrentPageName()){    
        taskForm.set("courseid", getCourseIdFromUrl());
        taskForm.set("taskid", getTaskIdFromUrl());
        apiCustomInputRequest(inputId, taskForm);
    } else if('submission' === getCurrentPageName()){
        $.get('/api/custom_input/',{
            submission: getTaskIdFromUrl()
        }, (result) => {
            taskForm.set("courseid", result['courseid']);
            taskForm.set("taskid", result['taskid']);
            apiCustomInputRequest(inputId, taskForm);
        }) 
    }
    $.post('/api/analytics/', {service: {"key": "custom_input", "name": "Custom input"}});
}
