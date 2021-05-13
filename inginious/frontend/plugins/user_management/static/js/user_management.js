const USER_INFORMATION_TABLE_ID = "userInformation";
const NEW_USERNAME_INPUT_ID = "newUsernameInput";
const NEW_NAME_INPUT_ID = "newNameInput";
const NEW_EMAIL_INPUT_ID = "newEmailInput";
const USERNAME_OR_EMAIL_INPUT_ID = "usernameOrEmailInput";
const USER_SETTINGS_ID = "userSettings";
const CHECK_BTN_ID = "checkBtn";

function addEvents() {
    allowEdit();
    addCheckBtnListener();
}

function allowEdit() {
    $(".edit").on("click", function () {
        const inputId = $(this).attr("data-action");
        const input = $(inputId);
        const isReadonly = input.prop("readonly");

        input.prop("readonly", !isReadonly);
        if (isReadonly) {
            input.trigger("focus");
        }
    })
}

function addCheckBtnListener() {
    function fillInput(id, content) {
        $(`#${id}`).val(content);
    }

    $(`#${CHECK_BTN_ID}`).on("click", function () {
        const usernameOrEmail = checkParameter();
        $.get("/api/user_management", {
            username_or_email: usernameOrEmail
        }, function (data) {
            const noDataMessageKey = "message";
            if (data.hasOwnProperty(noDataMessageKey)) {
                //TODO: display message
                return;
            }
            setupElements();
            $(`#${USER_SETTINGS_ID}`).show();
            fillInput(NEW_USERNAME_INPUT_ID, data["username"]);
            fillInput(NEW_NAME_INPUT_ID, data["name"]);
            fillInput(NEW_EMAIL_INPUT_ID, data["email"]);
            fillTable(data["count"]);
        })
    });
}

function fillTable(count) {
    function makeTableItem(key, value) {
        return `<tr><td><h5><b>${key}</b></h5></td><td><h5>${value}</h5></td></tr>`;
    }

    for (const [key, value] of Object.entries(count)) {
        $(`#${USER_INFORMATION_TABLE_ID}`).append(makeTableItem(key,value));
    }
}

function checkParameter() {
    const usernameOrEmail = $(`#${USERNAME_OR_EMAIL_INPUT_ID}`).val();
    if (usernameOrEmail) {
        return usernameOrEmail;
    } else {
        //TODO: Display error message
    }
}

function setupElements() {
    const userInfoTable = $(`#${USER_INFORMATION_TABLE_ID}`);

    $(".edit").each(function (_, obj) {
        const input = $($(obj).attr("data-action"));

        input.prop("readonly", true);
        input.attr("value", "");

    });

    userInfoTable.empty();
    $(`#${USER_SETTINGS_ID}`).hide();
}


$(function () {
    setupElements()
    addEvents();
});