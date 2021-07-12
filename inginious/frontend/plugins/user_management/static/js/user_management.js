const NEW_USERNAME_INPUT_ID = "newUsernameInput";
const NEW_NAME_INPUT_ID = "newNameInput";
const NEW_EMAIL_INPUT_ID = "newEmailInput";
const USER_SETTINGS_ID = "userSettings";
const NOTIFICATIONS_ID = "notificationsDiv";

let currentEmail = "";
let currentName = "";
let currentUsername = "";
let currentCollectionList = [];
let timeInterval;

function addEvents() {
    allowEdit();
    addSearchBtnListener();
    addListenerUpdateBtn();
    ajaxSetup();
    addSearchInputEnterListener();
    toggleEditTextListener();
}

function ajaxSetup() {
    $.ajaxSetup({
        beforeSend: function () {
            new MessageBox(NOTIFICATIONS_ID, "Loading...", "info", false);
        },
        error: function () {
            mainScrollToTop();
        }
    });
}

function cleanNotifications() {
    $(`#${NOTIFICATIONS_ID}`).empty();
}

function resetElements() {
    cleanBasicDataInputs();
    cleanUserInfoTable();
    hideUserSettingsDiv();
    cleanCurrentValues();
    closeTimeInterval();
    cleanNotifications();
    configUserTable();
}

function cleanBasicDataInputs() {
    $(".edit").each(function (_, obj) {
        const input = $($(obj).attr("data-action"));

        input.prop("readonly", true);
        input.attr("value", "");

    });
}

function cleanCurrentValues() {
    currentEmail = "";
    currentName = "";
    currentUsername = "";
    currentCollectionList = [];
}

function removeErrorStyle(inputObj) {
    const inputObjParent = inputObj.parent();

    inputObjParent.removeClass("has-error");
    inputObjParent.find("span").remove();
}

function checkTextLen(text, minLen) {
    return text.length >= minLen
}

function addErrorStyle(inputObj, errorText) {
    const inputObjParent = inputObj.parent();

    inputObjParent.addClass("has-error");
    inputObjParent.append(`<span class=\"help-block\">${errorText}</span>`);
}

function mainScrollToTop() {
    $(window).scrollTop(0);
}

function toggleEditTextListener() {
    $(".edit").on("click", function () {
        const currentContent = $(this).html();
        if (currentContent.includes(doneEditingText)) {
            $(this).html(`<i class="fa fa-pencil" aria-hidden="true"></i>${editText}</a></td>`);
        } else {
            $(this).html(`<i class="fa fa-floppy-o" aria-hidden="true"></i>${doneEditingText}</a></td>`);
        }
    });
}

$(function () {
    resetElements()
    addEvents();
});