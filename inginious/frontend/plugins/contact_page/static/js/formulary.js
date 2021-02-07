const SELECT_ID = "subject-selection";
const NO_SELECTED_ID = "subject-no-selected";
const PROBLEM_OR_COMMENT_ID = "subject-comment";
const NEW_COURSE_ID = "subject-new-course";
const EMAIL_INPUT_ID = "email-input";
const NAME_INPUT_ID = "name-input";
const CHECKBOX_ID = "checkbox-edit";
const COURSE_NAME_ID = "course-name";
const COURSE_NAME_SPACE_ID = "course-space";
const TEXTAREA_ID = "textarea-contact-page";
const SEND_BUTTON_ID = "send-contact-page-button";
const COMMENTS_INSTRUCTIONS_ID = "description-comment";
const NEW_COURSE_INSTRUCTIONS_ID = "description-new-course";
const ALERT_SPACE_ID = "alert-space";

class Formulary {
    constructor() {
        this.selectGroup = $(`#${SELECT_ID}`);
        this.emailInput = $(`#${EMAIL_INPUT_ID}`);
        this.nameInput = $(`#${NAME_INPUT_ID}`);
        this.editCheckbox = $(`#${CHECKBOX_ID}`);
        this.courseNameInput = $(`#${COURSE_NAME_ID}`);
        this.courseNameSpace = $(`#${COURSE_NAME_SPACE_ID}`);
        this.textarea = $(`#${TEXTAREA_ID}`);
        this.sendButton = $(`#${SEND_BUTTON_ID}`);
        this.commentInstructions = $(`#${COMMENTS_INSTRUCTIONS_ID}`);
        this.newCourseInstructions = $(`#${NEW_COURSE_INSTRUCTIONS_ID}`);
        this.configForm();
        this.addChangeListenerToSelect();
        this.addChangeListenerToCheckbox();
        this.addClickListenerToSendButton();
    }

    configForm() {
        this.hideAllSpecialSpaces();
        this.showSpecialSpaces();
    }


    hideAllSpecialSpaces() {
        this.courseNameSpace.hide();
        this.newCourseInstructions.hide();
        this.commentInstructions.hide();
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

    sendInfo() {
        if (this.validateFieldsStatus()) {
            this.sendRequest();
        } else {
            new MessageBox(ALERT_SPACE_ID, "Correct all the errors noted in order to send the message ", "warning", false);
        }
    }

    validateFieldsStatus() {
        this.removeErrorStyle(this.selectGroup);
        this.removeErrorStyle(this.emailInput);
        this.removeErrorStyle(this.nameInput);
        this.removeErrorStyle(this.textarea);
        return this.checkSubjectIsOk() & this.checkEmailFieldIsOk() & this.checkNameFieldIsOk() & this.checkTextAreaIsOk();
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
                new MessageBox(ALERT_SPACE_ID, "The message has been sent", "info", false);
            },
            error: function (request, status, error) {
                new MessageBox(ALERT_SPACE_ID, "The message could not be sent", "danger", false);
            }
        });
    }

    addErrorStyle(inputObj, errorText) {
        const inputObjParent = inputObj.parent();

        inputObjParent.addClass("has-error");
        inputObjParent.append(`<span class=\"help-block\">${errorText}</span>`);
    }

    removeErrorStyle(inputObj) {
        const inputObjParent = inputObj.parent();

        inputObjParent.removeClass("has-error");
        inputObjParent.find("span").remove();
    }

    checkSubjectIsOk() {
        if (!this.checkSubjectIsSelected()) {
            this.addErrorStyle(this.selectGroup, "Select an option");
            return false;
        }
        return true;
    }

    checkEmailFieldIsOk() {
        if (!this.checkInputContent(this.emailInput, 0)) {
            this.addErrorStyle(this.emailInput, "The email field is required");
            return false;
        }
        if (!this.validateEmailFormat()) {
            this.addErrorStyle(this.emailInput, "An email is requested");
            return false;
        }
        return true;
    }

    checkNameFieldIsOk() {
        if (!this.checkInputContent(this.nameInput, 0)) {
            this.addErrorStyle(this.nameInput, "The name field is required");
            return false;
        }
        return true;
    }

    checkTextAreaIsOk() {
        if (!this.checkInputContent(this.textarea, 21)) {
            this.addErrorStyle(this.textarea, "The comment is too short");
            return false;
        }
        return true;
    }

    checkSubjectIsSelected() {
        return this.getOptionSelected() !== NO_SELECTED_ID;
    }

    checkInputContent(inputObj, minLen) {
        return inputObj.val().length > minLen;
    }

    validateEmailFormat() {
        const emailFormat = /^[A-Z0-9._%+-]+@([A-Z0-9-]+\.)+[A-Z0-9._%+-]/i;
        return emailFormat.test(this.emailInput.val());
    }

    getOptionSelected() {
        return $(`#${SELECT_ID} option:selected`).attr("id");
    }


    changeSelection(optionId = NO_SELECTED_ID) {
        $(`#${optionId}`).attr('selected', 'selected');
    }


}