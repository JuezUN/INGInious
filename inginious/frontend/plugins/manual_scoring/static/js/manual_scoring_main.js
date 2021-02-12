const languages = {
    "java7": "java",
    "java8": "java",
    "cpp": "cpp",
    "cpp11": "cpp",
    "c": "c",
    "c11": "c",
    "python3": "python",
    "vhdl": "vhdl",
    "verilog": "verilog"
};
const responseFieldId = "grade_edit_submit_status";
const feedbackFieldId = "task_alert";

function save(rubric) {
    const contentInfo = "Submission graded and stored";
    const contentDanger = "Something went wrong";
    const txtComment = document.getElementById("text_comment");

    jQuery.ajax({
        success: function (data) {
            const message = new MessageBox(responseFieldId, contentInfo, "info");
        },
        method: "POST",
        data: {
            "manual_grade": rubric.score.toFixed(1),
            "comment": txtComment.value,
            "rubric": JSON.stringify(rubric.getSelectedFieldIds())
        },

        error: function (request, status, error) {
            console.log(error);
            const message = new MessageBox(responseFieldId, contentDanger, "danger");
        }
    });
}

function loadFeedBack() {
    const feedbackContent = getHtmlCodeForFeedback();
    const feedbackType = getTextBoxTypeBasedOnResult();
    const message = new MessageBox(feedbackFieldId, feedbackContent, feedbackType, false);
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
    })
}

function isRubricScoringPage() {
    const userKeyRegExp = new RegExp("[a-z0-9A-Z\\-_]+/admin/[a-z0-9A-Z\\-_]+/manual_scoring/task/[a-z0-9A-Z\\-_]+/submission/[a-z0-9A-Z\\-_]+");
    return userKeyRegExp.test(document.location.href);
}

jQuery(document).ready(function () {
    if (isRubricScoringPage()) {
        new CodeField();
        const rubric = new Rubric();
        let rubric_status = rubricStatus();
        rubric_status = JSON.parse(rubric_status.replace(/&quot;/g, '"'));
        rubric.loadSelectedFields(rubric_status);
        addToggleBehaviorToProblemDescription();
        loadFeedBack();
        addSaveFunctionToSaveButton(rubric);
    }
    window.save = save;
});


