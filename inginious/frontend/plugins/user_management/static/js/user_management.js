const USER_INFORMATION_TABLE_ID = "userInformation";
const NEW_USERNAME_INPUT_ID = "newUsernameInput";
const NEW_NAME_INPUT_ID = "newNameInput";
const NEW_EMAIL_INPUT_ID = "newEmailInput";
const USERNAME_OR_EMAIL_INPUT_ID = "usernameOrEmailInput";
const USER_SETTINGS_ID = "userSettings";
const CHECK_BTN_ID = "checkBtn";
const NOTIFICATIONS_ID = "notificationsDiv";

let currentEmail = "";
let currentName = "";
let currentUsername = "";
let currentCollectionList = [];

function addEvents() {
    allowEdit();
    addCheckBtnListener();
    addListenerUpdateBtn();
}

function configElements() {
    const userInfoTable = $(`#${USER_INFORMATION_TABLE_ID}`);

    $(".edit").each(function (_, obj) {
        const input = $($(obj).attr("data-action"));

        input.prop("readonly", true);
        input.attr("value", "");

    });

    userInfoTable.empty();
    $(`#${USER_SETTINGS_ID}`).hide();
    cleanCurrentValues();

}

function cleanCurrentValues() {
    currentEmail = "";
    currentName = "";
    currentUsername = "";
    currentCollectionList = [];
}

$(function () {
    configElements()
    addEvents();
});