jQuery(document).ready(function () {
    const codeField = new CodeField(CODE_AREA_ID, NOTEBOOK_CODE_AREA_ID, environmentType());
    const rubric = new Rubric();
    const currentGrade = $(`#${GRADE_ID}`).data("grade");
    const grade = new Score(GRADE_ID, currentGrade);
    let rubricStatusIds = rubricStatus();

    codeField.displayCodeArea();

    rubricStatusIds = JSON.parse(rubricStatusIds.replace(/&quot;/g, "\""));
    rubric.loadSelectedFields(rubricStatusIds);

    loadFeedBack(FEEDBACK_FIELD_ID);
    addToggleBehaviorToProblemDescription(TASK_NAME, TASK_DESCRIPTION_TEXT_ID);

    grade.changeColor();
    grade.updateScore();
});