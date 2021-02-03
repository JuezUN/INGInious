const SELECT_ID = "subject-selection";
const NO_SELECTED_ID = "subject-no-selected";
const PROBLEM_OR_COMMENT_ID = "subject-comment";
const NEW_COURSE_ID = "subject-new-course";
const EMAIL_INPUT_ID = "email-input";
const NAME_INPUT_ID = "name-input";
const CHECKBOX_ID = "checkbox-edit";
const CHECKBOX_SPACE_ID = "checkbox-space";
const COURSE_NAME_ID = "course-name";
const COURSE_NAME_SPACE_ID = "course-space";
const TEXTAREA_ID = "textarea-contact-page";
const SEND_BUTTON_ID = "send-contact-page-button";
const COMMENTS_INSTRUCTIONS = "description-comment";
const NEW_COURSE_INSTRUCTIONS = "description-new-course";


class Formulary {
    constructor() {
        this.selectGroup = $(`#${SELECT_ID}`);
        this.emailInput = $(`#${EMAIL_INPUT_ID}`);
        this.nameInput = $(`#${NAME_INPUT_ID}`);
        this.editCheckbox = $(`#${CHECKBOX_ID}`);
        this.checkBoxSpace = $(`#${CHECKBOX_SPACE_ID}`);
        this.courseNameInput = $(`#${COURSE_NAME_ID}`);
        this.courseNameSpace = $(`#${COURSE_NAME_SPACE_ID}`);
        this.textarea = $(`#${TEXTAREA_ID}`);
        this.sendButton = $(`#${SEND_BUTTON_ID}`);
        this.commentInstructions = $(`#${COMMENTS_INSTRUCTIONS}`);
        this.newCourseInstructions = $(`#${NEW_COURSE_INSTRUCTIONS}`);
        this.configForm();
    }

    addChangeListenerToSelect() {
        const self = this;
        this.selectGroup.change(function () {
            self.configForm();
        });
    }

    addChangeListenerToCheckbox() {
        const self = this;
        this.editCheckbox.change(function () {
            self.lockOrUnlockEmailAndNameInputF();
        });
    }

    addClickListenerToSendButton() {
        const self = this;
        this.sendButton.click(function () {
            self.sendInfo();
        });
    }

    lockOrUnlockEmailAndNameInputF() {
        if (this.editCheckbox.is(":checked")) {
            this.emailInput.prop("disabled", false);
            this.nameInput.prop("disabled", false);
        } else {
            this.emailInput.prop("disabled", true);
            this.nameInput.prop("disabled", true);
        }
    }

    getOptionSelected() {
        return $(`#${SELECT_ID} option:selected`).attr("id");
    }

    configForm() {
        this._hideAllSpecialSpaces();
        this.showSpecialSpaces();
    }

    showSpecialSpaces() {
        switch (this.getOptionSelected()) {
            case PROBLEM_OR_COMMENT_ID:
                this.commentInstructions.show();
                break;
            case NEW_COURSE_ID:
                this.courseNameSpace.show();
                this.newCourseInstructions.show();
                break;
            case NO_SELECTED_ID:
                //Do Nothing
                break;
        }
    }

    _hideAllSpecialSpaces() {
        this.courseNameSpace.hide();
        this.newCourseInstructions.hide();
        this.commentInstructions.hide();
    }

    isLoggedIn() {
        return Boolean(this.checkBoxSpace.attr("data-isLoggedIn"))
    }

    changeSelection(optionId = NO_SELECTED_ID) {
        $(`#${optionId}`).attr('selected', 'selected');
    }

    sendInfo() {
        if (this.checkFieldStatus()) {
            this.sendRequest();
        }
    }

    sendRequest() {
        jQuery.ajax({
            method: "POST",
            data: {
                "subject_id": this.getOptionSelected(),
                "email": this.emailInput.val(),
                "name": this.nameInput.val(),
                "courseName": this.courseNameInput.val(),
                "textarea": this.textarea.val()

            },
            success: function (data) {
                //TODO
            },
            error: function (request, status, error) {
                //TODO
            }
        });
    }

    checkFieldStatus() {
        //TODO
        return true;
    }
}