const SELECT_ID = "subject-selection";
const NO_SELECTED_ID = "subject-no-selected";
const PROBLEM_OR_COMMENT_ID = "subject-comment";
const NEW_COURSE_ID = "subject-new-course";
const EMAIL_INPUT_ID = "email-input";
const NAME_INPUT_ID = "name-input";
const CHECKBOX_ID = "checkbox-edit";
const COURSE_NAME_ID = "course-name";
const COURSE_GROUP_ID = "course-group";
const COURSE_NAME_SPACE_ID = "course-space";
const TEXTAREA_ID = "textarea-contact-page";
const SEND_BUTTON_ID = "send-contact-page-button";
const COMMENTS_INSTRUCTIONS_ID = "description-comment";
const NEW_COURSE_INSTRUCTIONS_ID = "description-new-course";
const ALERT_HAS_ERRORS_ID = "alert-has-errors";
const MODAL_SEND_ID = "modalSendMessage";
const ALERT_MODAL_ID = "alert-onmodal";
const TEXT_ALERT_ON_MODAL_SUCCESS_ID = "text-alert-modal-success";
const TEXT_ALERT_ON_MODAL_FAIL_ID = "text-alert-modal-fail";
const BUTTON_MORE_DETAILS = "button-more-details";
const DETAILS_DIV = "details";
const DETAILS_COLLAPSE = "details-text";
const ERROR_TEXT = "error";


class ContactPageForm {
    constructor() {
        this.selectGroup = $(`#${SELECT_ID}`);
        this.emailInput = $(`#${EMAIL_INPUT_ID}`);
        this.nameInput = $(`#${NAME_INPUT_ID}`);
        this.editCheckbox = $(`#${CHECKBOX_ID}`);
        this.courseNameInput = $(`#${COURSE_NAME_ID}`);
        this.courseGroupInput = $(`#${COURSE_GROUP_ID}`);
        this.courseNameSpace = $(`#${COURSE_NAME_SPACE_ID}`);
        this.textarea = $(`#${TEXTAREA_ID}`);
        this.sendButton = $(`#${SEND_BUTTON_ID}`);
        this.commentInstructions = $(`#${COMMENTS_INSTRUCTIONS_ID}`);
        this.newCourseInstructions = $(`#${NEW_COURSE_INSTRUCTIONS_ID}`);
        this.modalSendMessage = $(`#${MODAL_SEND_ID}`);
        this.alertOnModal = $(`#${ALERT_MODAL_ID}`);
        this.textOnAlertSuccess = $(`#${TEXT_ALERT_ON_MODAL_SUCCESS_ID}`);
        this.textOnAlertFail = $(`#${TEXT_ALERT_ON_MODAL_FAIL_ID}`);
        this.buttonMoreDetails = $(`#${BUTTON_MORE_DETAILS}`);
        this.details = $(`#${DETAILS_DIV}`);
        this.errorText = $(`#${ERROR_TEXT}`);
        this.detailsText = $(`#${DETAILS_COLLAPSE}`);
        this.alertOnErrorValidation = $(`#${ALERT_HAS_ERRORS_ID}`)
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
            self.sendButton.prop("disabled",true);
        });
    }

    addCloseListenerToOnCloseModal() {
        const self = this;
        this.modalSendMessage.on("hidden.bs.modal", function() {
            if (self.alertOnModal.is('.alert-success')) {
                if (self.editCheckbox.is(":checked")) {
                    self.emailInput.val('');
                    self.nameInput.val('');
                }
                self.courseNameInput.val('');
                self.courseGroupInput.val('');
                self.textarea.val('');
                self.alertOnModal.removeClass('alert-success');
                self.textOnAlertSuccess.hide();
            } 
            if (self.alertOnModal.is('.alert-danger')) {
                self.alertOnModal.removeClass('alert-danger');
                self.textOnAlertFail.hide();
                self.errorText.text('');
                self.details.hide();
                self.detailsText.collapse('hide');
            }
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
            this.alertOnErrorValidation.hide();
            this.sendRequest();
            this.sendContactPageAnalytics();
        } else {
            this.alertOnErrorValidation.show();
        }
    }

    sendContactPageAnalytics() {
        jQuery.post("/api/analytics/", {
            service: {
                key: "contact_page",
                name: "Contact us"
            },
        });
    }

    validateFieldsStatus() {
        this.removeErrorStyle(this.selectGroup);
        this.removeErrorStyle(this.emailInput);
        this.removeErrorStyle(this.nameInput);
        this.removeErrorStyle(this.textarea);
        return this.checkSubjectIsOk() & this.checkEmailFieldIsOk() & this.checkNameFieldIsOk() & this.checkTextAreaIsOk();
    }

    sendRequest() {
        const self = this;
        jQuery.ajax({
            method: "POST",
            data: {
                "subject_id": this.getOptionSelected(),
                "email": this.emailInput.val(),
                "name": this.nameInput.val(),
                "courseName": this.courseNameInput.val(),
                "courseGroup":this.courseGroupInput.val(),
                "textarea": this.textarea.val()
            },
            success: function (data) { 
                self.alertOnModal.addClass('alert-success');
                self.textOnAlertSuccess.show();
                self.addCloseListenerToOnCloseModal();
                self.modalSendMessage.modal("show"); 
            },
            error: function (request, status, error) {
                self.alertOnModal.addClass('alert-danger');
                self.textOnAlertFail.show();
                self.addCloseListenerToOnCloseModal();
                self.modalSendMessage.modal("show");
                self.errorText.text(request.status+ " " + error);
                self.details.show();
            }
        });
    }

    addErrorStyle(inputObj, errorText) {
        const inputObjParent = inputObj.parent(); 
        inputObjParent.addClass("has-error");
        const error = $(`#${errorText}`);
        error.show();
    }

    removeErrorStyle(inputObj) {
        const inputObjParent = inputObj.parent();
        inputObjParent.removeClass("has-error");
        inputObjParent.find("p.help-block").hide();
    }

    checkSubjectIsOk() {
        if (!this.checkSubjectIsSelected()) {
            this.addErrorStyle(this.selectGroup, "error-subject-no-selected");
            return false;
        }
        return true;
    }

    checkEmailFieldIsOk() {
        if (!this.checkInputContent(this.emailInput, 0)) {
            this.addErrorStyle(this.emailInput, "error-email-required");
            return false;
        }
        if (!this.validateEmailFormat()) {
            this.addErrorStyle(this.emailInput, "error-email-not-email");
            return false;
        }
        return true;
    }

    checkNameFieldIsOk() {
        if (!this.checkInputContent(this.nameInput, 0)) {
            this.addErrorStyle(this.nameInput, "error-name-required");
            return false;
        }
        return true;
    }

    checkTextAreaIsOk() {
        if (!this.checkInputContent(this.textarea, 21)) {
            this.addErrorStyle(this.textarea, "error-textarea-ok");
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
        $(`#${optionId}`).attr("selected", "selected");
    }

}
