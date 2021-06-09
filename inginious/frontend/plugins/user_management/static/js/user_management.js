const NEW_USERNAME_INPUT_ID = "newUsernameInput";
const NEW_NAME_INPUT_ID = "newNameInput";
const NEW_EMAIL_INPUT_ID = "newEmailInput";
const USERNAME_OR_EMAIL_INPUT_ID = "usernameOrEmailInput";
const USER_SETTINGS_ID = "userSettings";
const NOTIFICATIONS_ID = "notificationsDiv";

let currentEmail = "";
let currentName = "";
let currentUsername = "";
let currentCollectionList = [];
let timeInterval;

function addEvents() {
    allowEdit();
    addCheckBtnListener();
    addListenerUpdateBtn();
    ajaxSetup();
}

function ajaxSetup() {
    $.ajaxSetup({
        beforeSend: function () {
            new MessageBox(NOTIFICATIONS_ID, "Loading...", "info", false);
        }
    });
}

function cleanNotifications() {
    $(`#${NOTIFICATIONS_ID}`).empty();
}

function configElements() {

    $(".edit").each(function (_, obj) {
        const input = $($(obj).attr("data-action"));

        input.prop("readonly", true);
        input.attr("value", "");

    });

    cleanUserInfoTable();
    hideUserSettings();
    cleanCurrentValues();
    closeInterval();
    cleanNotifications();
    configUserTable();
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

$(function () {
    configElements()
    addEvents();
});