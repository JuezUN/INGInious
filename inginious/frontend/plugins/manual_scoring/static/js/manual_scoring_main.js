const RESPONSE_FIELD_ID = "grade_edit_submit_status";
const FEEDBACK_FIELD_ID = "task_alert";

function save(rubric) {
    const contentInfo = "Submission graded and stored";
    const contentDanger = "Something went wrong";
    const txtComment = document.getElementById("text_comment");

    jQuery.ajax({
        success: function (data) {
            const message = new MessageBox(RESPONSE_FIELD_ID, contentInfo, "info");
        },
        method: "POST",
        data: {
            "manual_grade": rubric.score.toFixed(1),
            "comment": txtComment.value,
            "rubric": JSON.stringify(rubric.getSelectedFieldIds())
        },

        error: function (request, status, error) {
            const message = new MessageBox(RESPONSE_FIELD_ID, contentDanger, "danger");
        }
    });
}

function loadFeedBack() {
    const feedbackContent = getHtmlCodeForFeedback();
    const feedbackType = getTextBoxTypeBasedOnResult();
    const message = new MessageBox(FEEDBACK_FIELD_ID, feedbackContent, feedbackType, false);
    message.deleteCloseButton();
}


function addToggleBehaviorToProblemDescription() {
    $("#info").click(function () {
        $("#text-context").collapse("toggle");
    });
}

function addSaveFunctionToSaveButton(rubric) {
    $("#save_button").click(function () {
        save(rubric);
    });
}

function isRubricScoringPage() {
    const userKeyRegExp = new RegExp("[a-z0-9A-Z\\-_]+/admin/[a-z0-9A-Z\\-_]+/manual_scoring/task/[a-z0-9A-Z\\-_]+/submission/[a-z0-9A-Z\\-_]+");
    return userKeyRegExp.test(document.location.href);
}

jQuery(document).ready(function () {
    if (isRubricScoringPage()) {
        const condeField = new CodeField();
        const rubric = new Rubric();
        let rubricStatusIds = rubricStatus();
        rubricStatusIds = JSON.parse(rubricStatusIds.replace(/&quot;/g, "\""));
        rubric.loadSelectedFields(rubricStatusIds);
        addToggleBehaviorToProblemDescription();
        loadFeedBack();
        addSaveFunctionToSaveButton(rubric);
    }
    window.save = save;
});


