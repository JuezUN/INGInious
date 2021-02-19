const RESPONSE_FIELD_ID = "gradeEditSubmitStatus";
const FEEDBACK_FIELD_ID = "taskAlert";
const TASK_NAME = "taskName";
const TASK_DESCRIPTION_TEXT_ID = "taskDescription";
const CODE_AREA_ID = "codemirrorTextArea";
const NOTEBOOK_CODE_AREA_ID = "notebookHolder";

function loadFeedBack(feedbackFieldId) {
    const feedbackContent = getHtmlCodeForFeedback();
    const feedbackType = getTextBoxTypeBasedOnResult();
    const message = new MessageBox(feedbackFieldId, feedbackContent, feedbackType, false);
    message.deleteCloseButton();
}


function addToggleBehaviorToProblemDescription(taskName, taskDescription) {
    $(`#${taskName}`).click(function () {
        $(`#${taskDescription}`).collapse("toggle");
    });
}