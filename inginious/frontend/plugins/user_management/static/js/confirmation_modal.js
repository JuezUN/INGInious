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

    $(`#${UPDATE_BTN_ID}`).off('click').on("click", function () {
        requestToUpdate = validateInputs();
        if (!dictionaryIsEmpty(requestToUpdate)) {
            configModal();
            confirmListener();
        } else {
            new MessageBox(NOTIFICATIONS_ID, inputGeneralError, "danger", false);
            mainScrollToTop();
        }
    });
}

function configModal() {
    $(`#${MODAL_ID}`).modal("show");
    $(`#${USERNAME_TEXT_ID}`).html(currentUsername);
    $(`#${CONFIRMATION_INPUT_ID}`).val("")
}

function confirmListener() {
    function dataToString(data) {
        let string = "";
        for (const [key, value] of Object.entries(data)) {
            string += `<li><b>${wordsDictionary[key]}:</b> ${value}</li>`;
        }
        return `<ul class="normalList">${string}</ul>`;
    }

    $(`#${UPDATE_CONFIRM_ID}`).off('click').on("click", function () {
        requestToUpdate["username"] = currentUsername;
        requestToUpdate["email"] = currentEmail;
        if (checkConfirmationInput()) {
            hideModal();
            mainScrollToTop();
            disableSettings(true);
            $.post("/api/user_management", requestToUpdate, function (data) {
                const message = `<strong>${successMessage}:</strong> ${dataToString(data)}`;
                resetElements();
                new MessageBox(NOTIFICATIONS_ID, message, "success", false);
            }).fail((xhr, status, error) => {
                const response = JSON.parse(xhr.responseText);
                const message = `<strong>${errorText}:</strong> ${dataToString(response)}`;
                new MessageBox(NOTIFICATIONS_ID, message, "danger", false);
            }).done(() => {
                disableSettings(false);
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
        requestToUpdate["collection_list"] = JSON.stringify(currentCollectionList);
        addListElement(createListElement(wordsDictionary["username"]));
    }
    if (checkName()) {
        requestToUpdate["name"] = getInputValue(NEW_NAME_INPUT_ID);
        addListElement(createListElement(wordsDictionary["name"]));
    }
    if (checkEmailInput()) {
        requestToUpdate["new_email"] = getInputValue(NEW_EMAIL_INPUT_ID);
        addListElement(createListElement(wordsDictionary["email"]));
    }
    return requestToUpdate;
}

function cleanList() {
    $(`#${PARAMETERS_LIST_ID}`).empty();
}

function hideModal() {
    $(`#${MODAL_ID}`).modal("hide");
}