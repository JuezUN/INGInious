const UPDATE_BTN_ID = "updateBtn";
const UPDATE_CONFIRM_ID = "updateDataConfirmBtn";
const MODAL_ID = "uploadModal";
const PARAMETERS_LIST_ID = "listParametersChanged";
const USERNAME_TEXT_ID = "usernameToConfirm";
const CONFIRMATION_INPUT_ID = "usernameInputConfirmation";
let requestToUpdate = {};

function addListenerUpdateBtn() {
    function dictionaryIsEmpty(dict) {
        return Object.keys(dict).length === 0;
    }

    $(`#${UPDATE_BTN_ID}`).on("click", function () {
        requestToUpdate = validateInputs();
        if (!dictionaryIsEmpty(requestToUpdate)) {
            configModal();
            confirmListener();
        } else {
            new MessageBox(NOTIFICATIONS_ID, "No modification has been made", "danger", false);
        }
    });
}

function configModal() {
    $(`#${MODAL_ID}`).modal("show");
    $(`#${USERNAME_TEXT_ID}`).html(currentUsername);
}

function confirmListener() {
    $(`#${UPDATE_CONFIRM_ID}`).on("click", function () {
        requestToUpdate["username"] = currentUsername;
        if (checkConfirmationInput()) {
            $.post("/api/user_management", requestToUpdate, function () {
                $(`#${MODAL_ID}`).modal("hide");
                new MessageBox(NOTIFICATIONS_ID, "OK", "success", false);
            });
        }
    });
}

function checkConfirmationInput() {
    const inputText = $(`#${CONFIRMATION_INPUT_ID}`);
    removeErrorStyle(inputText);
    if (inputText.val() === currentUsername) {
        return true;
    } else {
        addErrorStyle(inputText, usernameMatchError);
        return false;
    }
}

function createListElement(text) {
    return `<li><b>${text}</b></li>`;
}

function addListElement(liElement) {
    $(`#${PARAMETERS_LIST_ID}`).append(liElement);
}

function validateInputs() {
    requestToUpdate = {};
    cleanList();
    if (checkUsername()) {
        requestToUpdate["new_username"] = getInputValue(NEW_USERNAME_INPUT_ID);
        addListElement(createListElement(usernameText));
    }
    if (checkName()) {
        requestToUpdate["name"] = getInputValue(NEW_NAME_INPUT_ID);
        addListElement(createListElement(nameText));
    }
    if (checkEmailInput()) {
        requestToUpdate["email"] = getInputValue(NEW_EMAIL_INPUT_ID);
        addListElement(createListElement(emailText));
    }
    return requestToUpdate;
}

function cleanList() {
    $(`#${PARAMETERS_LIST_ID}`).empty();
}