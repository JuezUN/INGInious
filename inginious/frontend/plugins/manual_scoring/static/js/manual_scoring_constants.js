const RESPONSE_FIELD_ID = "gradeEditSubmitStatus";
const FEEDBACK_FIELD_ID = "taskAlert";
const TASK_NAME = "taskName";
const TASK_DESCRIPTION_TEXT_ID = "taskDescription";
const CODE_AREA_ID = "codemirrorTextArea";
const NOTEBOOK_CODE_AREA_ID = "notebookHolder";
const FILE_MULTI_LANG_ID = "downloadMultiLang";
const GRADE_ID = "grade";

function loadFeedBack(feedbackFieldId) {
    const feedbackType = getTextBoxTypeBasedOnResult();
    const task_alert = $(`#${feedbackFieldId}`);
    jQuery.post(getURLSubmissionInput(), {
        "@action": "load_submission_input",
        "submissionid": getCurrentSubmissionId()
    }, null, "json")
        .done(function (data) {
            task_alert.html(getAlertCode(data.text, feedbackType, false));
        });

}


function addToggleBehaviorToProblemDescription(taskName, taskDescription) {
    $(`#${taskName}`).click(function () {
        $(`#${taskDescription}`).collapse("toggle");
    });
}