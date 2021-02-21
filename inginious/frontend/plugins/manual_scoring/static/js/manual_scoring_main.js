const COMMENTS_TEXT_AREA_ID = "textComments";
const SAVE_BUTTON_ID = "saveButton";

function save(rubric) {
    const contentInfo = "Submission graded and stored";
    const contentDanger = "Something went wrong";
    const txtComment = document.getElementById(COMMENTS_TEXT_AREA_ID);

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

function addSaveFunctionToSaveButton(rubric) {
    $(`#${SAVE_BUTTON_ID}`).click(function () {
        save(rubric);
    });
}

jQuery(document).ready(function () {
    const codeField = new CodeField(CODE_AREA_ID, NOTEBOOK_CODE_AREA_ID, environmentType());
    codeField.displayCodeArea();

    const rubric = new Rubric();
    let rubricStatusIds = rubricStatus();
    rubricStatusIds = JSON.parse(rubricStatusIds.replace(/&quot;/g, "\""));
    rubric.loadSelectedFields(rubricStatusIds);
    rubric.makeRubricInteractive();

    loadFeedBack(FEEDBACK_FIELD_ID);
    addToggleBehaviorToProblemDescription(TASK_NAME, TASK_DESCRIPTION_TEXT_ID);

    addSaveFunctionToSaveButton(rubric);

    const comment = new CodeField(COMMENTS_TEXT_AREA_ID);
    comment.showMultiLangCodeArea();
    window.save = save;
});


