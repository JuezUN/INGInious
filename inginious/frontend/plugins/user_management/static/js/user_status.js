const USER_SESSIONS_BADGE_ID = "userConnection";
const SUBMISSIONS_TABLE_ID = "userSubmissions";


function updateSubmissionStatus() {
    $.ajax({
        data: {
            username: currentUsername
        },
        type: "GET",
        url: "/api/user_status",
        success: function (data) {
            _updateSubmissionTable(data);
            _updateBadge(data["num_connections"]);
        },
        beforeSend(jqXHR, settings) {
            // break default setting
        }
    })
}

function _updateSubmissionTable(data) {
    const submissionsArray = data["submissions"];
    const customTestArray = data["custom_test"];

    cleanSubmissionsTable();

    if (!submissionsArray.length && !customTestArray.length) {
        _appendNoSubmissionsMessage();
    } else {
        _appendSubmissionsToTable("Submission", submissionsArray);
        _appendSubmissionsToTable("Custom Test", customTestArray);
    }
}

function _updateBadge(numberSessions) {
    const badge = $(`#${USER_SESSIONS_BADGE_ID}`);

    function toggleClass() {
        "label-danger label-success".split(" ").forEach(function (classString) {
            badge.toggleClass(classString);
        });
    }

    function restoreBadge() {
        if (badge.hasClass("label-success")) {
            toggleClass();
        }
        badge.text("");
    }

    restoreBadge();
    badge.text(numberSessions);
    if (numberSessions > 0) {
        toggleClass();
    }

}

function _appendSubmissionsToTable(type, submissionArray) {
    const table = $(`#${SUBMISSIONS_TABLE_ID}`);
    $.each(submissionArray, (_, submission) => {
        table.append(_createSubmissionItem(type, submission));
    });
}

function _createSubmissionItem(type, submission) {
    return `<tr><td>${type}</td><td>${submission["courseid"]}</td><td>${submission["taskid"]}</td><td>${submission["submitted_on"]}</td></tr>`;
}

function _appendNoSubmissionsMessage() {
    const noSubmissionsMessage = `<tr><td colspan="4" class="text-center"><h4>${noSubmissions}</h4></td></tr>`;
    $(`#${SUBMISSIONS_TABLE_ID}`).append(noSubmissionsMessage);
}

function cleanSubmissionsTable() {
    $(`#${SUBMISSIONS_TABLE_ID}`).empty();
}

function openTimeInterval() {
    return setInterval(updateSubmissionStatus, 3000);
}

function closeInterval() {
    clearInterval(timeInterval);
}

