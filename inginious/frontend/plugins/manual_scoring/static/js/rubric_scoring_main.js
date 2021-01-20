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

function commentSubmit() {
    const txtComment = document.getElementById("text_comment");
    const contentInfo = "Successfully saved";
    const contentDanger = "Error at saving Comment, please try again."
    const contentWarning = "Error at saving Comment, comment to long, max length of comment is 1000."
    const maxTam = 1000;

    if (txtComment.value.length > maxTam) {
        const message = new MessageBox(responseFieldId, contentWarning, "warning");
        return;
    }

    jQuery.ajax({
        success: function (data) {
            const message = new MessageBox(responseFieldId, contentInfo, "info");
        },
        method: "POST",

        data: {"comment": txtComment.value},

        error: function (request, status, error) {
            const message = new MessageBox(responseFieldId, contentDanger, "danger");
        }
    });
}

function save(rubric) {
    let contentInfo = "Submission graded and stored";
    let contentDanger = "Something went wrong";
    jQuery.ajax({
        success: function (data) {
            commentSubmit();
            const message = new MessageBox(responseFieldId, contentInfo, "info");
        },
        method: "POST",

        data: {"grade": rubric.score.toFixed(1)},

        error: function (request, status, error) {
            const message = new MessageBox(responseFieldId, contentDanger, "danger");
        }
    });
}

function loadFeedBack() {
    const feedbackContent = getHtmlCodeForFeedBack();
    const feedbackType = getTextBoxTypeBaseOnResult();
    new MessageBox(feedbackFieldId, feedbackContent, feedbackType, false);
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

function isRubricScoringPage(){
    const userKeyRegExp = new RegExp("[a-z0-9A-Z\\-_]+/admin/[a-z0-9A-Z\\-_]+/manual_scoring/task/[a-z0-9A-Z\\-_]+/submission/[a-z0-9A-Z\\-_]+");
    return userKeyRegExp.test(document.location.href);
}
jQuery(document).ready(function () {
    if (isRubricScoringPage()) {
        new CodeField();
        const rubric = new RubricScoring();
        addToggleBehaviorToProblemDescription();
        loadFeedBack();
        addSaveFunctionToSaveButton(rubric);
    }
    window.save = save;
});



