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
            updateScoreOnInfo(rubric.score);
            sendManualScoringAnalytics();
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

function updateScoreOnInfo(score) {
    const grade = new Score(GRADE_ID, score);
    grade.updateScore();
    grade.changeColor();
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

function sendManualScoringAnalytics() {
    $.post('/api/analytics/', {
        service: {
            key: "manual_scoring_creation",
            name: "Manual Scoring - Creation"
        },
        course_id: getCourseId(),
    });
}

jQuery(document).ready(function () {
    const codeField = new CodeArea(CODE_AREA_ID, NOTEBOOK_CODE_AREA_ID, environmentType());
    const rubric = new Rubric();
    const comment = new CodeArea(COMMENTS_TEXT_AREA_ID);
    const currentGrade = $(`#${GRADE_ID}`).data("grade");
    const grade = new Score(GRADE_ID, currentGrade);

    let rubricStatusIds = rubricStatus();

    codeField.displayCodeArea();

    rubricStatusIds = JSON.parse(rubricStatusIds.replace(/&quot;/g, "\""));
    rubric.loadSelectedFields(rubricStatusIds);
    rubric.makeRubricInteractive();

    loadFeedBack(FEEDBACK_FIELD_ID);
    addToggleBehaviorToProblemDescription(TASK_NAME, TASK_DESCRIPTION_TEXT_ID);

    addSaveFunctionToSaveButton(rubric);

    comment.showMultiLangCodeArea();
    previewCode();

    grade.changeColor();
    grade.updateScore();

    window.save = save;
});


