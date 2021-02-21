const COMMENTS_TEXT_AREA_ID = "textComments";
const SAVE_BUTTON_ID = "saveButton";
const PREVIEW_TAB_ID = "preview_tab";
const PREVIEW_AREA_ID = "preview_area";
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

function previewCode() {
    const contentDanger = "Something went wrong";
    const txtComment = document.getElementById(COMMENTS_TEXT_AREA_ID);
    $(`#${PREVIEW_TAB_ID}`).click(function () {
        $.ajax("/api/preview_content", {
            method: "POST",
            data: {
                content: txtComment.value
            },
            success: function (data) {
                $(`#${PREVIEW_AREA_ID}`).html(data);
            },
            error: function (request, status, error) {
                const message = new MessageBox(RESPONSE_FIELD_ID, contentDanger, "danger");
            }

        })
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
    previewCode();
    window.save = save;
});


