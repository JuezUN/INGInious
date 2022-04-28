const USER_INFORMATION_TABLE_ID = "userInformation";
const USER_TOTAL_TABLE_ID = "userInformationFoot";
const USER_COURSES_TABLE_ID = "userCoursesInformation";
const USER_INFORMATION_TITLE_ID = "userInformationTitle";

function fillUserTable(userInfoTable = 1,dataDict) {
    /*
    fills tables given a dictionary with the data.
    boolean parameter user_info_table determines wich of the two current tables in the user manager is being filled
    */
    function makeTableItem(key, value, valueInBold = false) {
        if (valueInBold)
            return `<tr><td><h5><b>${key}</b></h5></td><td><h5><b>${value}</b></h5></td></tr>`;
        return `<tr><td><h5><b>${key}</b></h5></td><td><h5>${value}</h5></td></tr>`;
    }

    if (userInfoTable){
        let total = 0;
        for (const [key, value] of Object.entries(dataDict)) {
            total += value;
            $(`#${USER_INFORMATION_TABLE_ID}`).append(makeTableItem(key, value));
        }
        $(`#${USER_TOTAL_TABLE_ID}`).append(makeTableItem("Total", total, true))
    }else{
        for (const [key, value] of Object.entries(dataDict)) {
            $(`#${USER_COURSES_TABLE_ID}`).append(makeTableItem(key, value));
        }
    }
}

function requestUserData(username, email) {
    function fillInput(id, content) {
        $(`#${id}`).val(content);
    }

    $.get("/api/user_management", {
        username,
        email
    }, function (data) {
        resetElements();
        getCurrentValues(data);
        updateSubmissionStatus();
        timeInterval = openTimeInterval();
        showUserSettings()
        fillInput(NEW_USERNAME_INPUT_ID, currentUsername);
        fillInput(NEW_NAME_INPUT_ID, currentName);
        fillInput(NEW_EMAIL_INPUT_ID, currentEmail);
        fillUserTable(1,data["count"]);
        fillUserTable(0,data["courses"]);
        alertForUnknownCollections(data["unknown_collections"]);
        fillUserInformationTitle(data);
    })
}

function showUserSettings() {
    $(`#${USER_SETTINGS_ID}`).show();
}

function hideUserSettingsDiv() {
    $(`#${USER_SETTINGS_ID}`).hide();
}

function getCurrentValues(data) {
    currentEmail = data["email"];
    currentName = data["name"];
    currentUsername = data["username"];
    currentCollectionList = Object.keys(Object.fromEntries(Object.entries(data["count"]).filter(([k, v]) => v > 0)));
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

function checkEmailFormat(emailText) {
    const emailFormat = /^[^@]+@[^@]+\.[A-Z0-9._-]/i;
    return emailFormat.test(emailText);
}

function checkEmailInput() {
    const emailInput = $(`#${NEW_EMAIL_INPUT_ID}`);
    removeErrorStyle(emailInput);
    if (hasEmailChanged()) {
        if (checkEmailFormat(emailInput.val())) {
            return true;
        } else {
            addErrorStyle(emailInput, emailFormatError);
            return false;
        }
    }
}

function checkUsernameFormat(usernameText) {
    const usernameFormat = /^[-_.|~0-9A-Z]{4,}$/i;
    return usernameFormat.test(usernameText);
}

function checkUsername() {
    const usernameInput = $(`#${NEW_USERNAME_INPUT_ID}`);
    const minLen = 4;

    removeErrorStyle(usernameInput);
    if (hasUsernameChanged()) {
        if (checkTextLen(usernameInput.val(), minLen)) {
            if (checkUsernameFormat(usernameInput.val())) {
                return true;
            } else {
                addErrorStyle(usernameInput, usernameFormatError);
                return false;
            }
        } else {
            addErrorStyle(usernameInput, inputLenError);
            return false;
        }
    }
    return false;
}

function checkName() {
    const name = $(`#${NEW_NAME_INPUT_ID}`);
    const minLen = 1;
    removeErrorStyle(name);
    if (hasNameChanged()) {
        if (checkTextLen(name.val(), minLen)) {
            return true;
        } else {
            addErrorStyle(name, inputLenError);
            return false;
        }
    }
    return false;
}

function hasUsernameChanged() {
    return $(`#${NEW_USERNAME_INPUT_ID}`).val() !== currentUsername;
}

function hasNameChanged() {
    return $(`#${NEW_NAME_INPUT_ID}`).val() !== currentName;
}

function hasEmailChanged() {
    return $(`#${NEW_EMAIL_INPUT_ID}`).val() !== currentEmail;
}

function getInputValue(inputId) {
    return $(`#${inputId}`).val();
}



function alertForUnknownCollections(unknownCollections) {
    if (unknownCollections.length) {
        new MessageBox(NOTIFICATIONS_ID, `${unknownCollectionsMessage}: ${unknownCollections}. ${pleaseCheck}`, "warning", false);
    }
}

function fillUserInformationTitle(userData) {
    const username = userData["username"];
    const name = userData["name"];
    $(`#${USER_INFORMATION_TITLE_ID}`).html(`${userInformationTitleText}: ${username} (${name})`);
}

function disableSettings(blockSettings) {
    $(`#${UPDATE_BTN_ID}`).prop("disabled", blockSettings);
    $(".edit").each(function (_, obj) {
        const inputId = $(obj).attr("data-action");
        const input = $(inputId);
        if (blockSettings) {
            input.prop("readonly", blockSettings);
            $(obj).html(`<i class="fa fa-pencil" aria-hidden="true"></i>${editText}</a></td>`);
            $(obj).addClass("disabled");
        } else {
            $(obj).removeClass("disabled");
        }
    });
}

