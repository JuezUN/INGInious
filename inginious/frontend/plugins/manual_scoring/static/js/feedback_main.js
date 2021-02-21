const COMMENTS_AREA = "codemirrorCommentArea";
jQuery(document).ready(function () {
    const codeField = new CodeField(CODE_AREA_ID, NOTEBOOK_CODE_AREA_ID, environmentType());
    codeField.displayCodeArea();

    const rubric = new Rubric();
    let rubricStatusIds = rubricStatus();
    rubricStatusIds = JSON.parse(rubricStatusIds.replace(/&quot;/g, "\""));
    rubric.loadSelectedFields(rubricStatusIds);

    loadFeedBack(FEEDBACK_FIELD_ID);
    addToggleBehaviorToProblemDescription(TASK_NAME, TASK_DESCRIPTION_TEXT_ID);
});