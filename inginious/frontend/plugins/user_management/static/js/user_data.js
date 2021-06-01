function addCheckBtnListener() {
    function fillInput(id, content) {
        $(`#${id}`).val(content);
    }

    $(`#${CHECK_BTN_ID}`).on("click", function () {
        const usernameOrEmail = checkSearchParameter();
        $.get("/api/user_management", {
            username_or_email: usernameOrEmail
        }, function (data) {
            const noDataMessageKey = "message";
            if (data.hasOwnProperty(noDataMessageKey)) {
                //TODO: display message
                return;
            }
            cleanNot()
            configElements();
            getCurrentValues(data);
            $(`#${USER_SETTINGS_ID}`).show();
            fillInput(NEW_USERNAME_INPUT_ID, currentUsername);
            fillInput(NEW_NAME_INPUT_ID, currentName);
            fillInput(NEW_EMAIL_INPUT_ID, currentEmail);
            fillUserTable(data["count"]);
        })
    });
}

function getCurrentValues(data) {
    currentEmail = data["email"];
    currentName = data["name"];
    currentUsername = data["username"];
    currentCollectionList = Object.keys(Object.fromEntries(Object.entries(data["count"]).filter(([k, v]) => v > 0)));
}

function checkSearchParameter() {
    const usernameOrEmail = $(`#${USERNAME_OR_EMAIL_INPUT_ID}`).val();
    if (usernameOrEmail) {
        return usernameOrEmail;
    } else {
        //TODO: Display error message
    }
}


function fillUserTable(count) {
    function makeTableItem(key, value) {
        return `<tr><td><h5><b>${key}</b></h5></td><td><h5>${value}</h5></td></tr>`;
    }

    for (const [key, value] of Object.entries(count)) {
        $(`#${USER_INFORMATION_TABLE_ID}`).append(makeTableItem(key, value));
    }
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

function checkTextLen(text, minLen) {
    return text.length >= minLen
}

function checkEmailInput() {
    const email = $(`#${NEW_EMAIL_INPUT_ID}`);
    removeErrorStyle(email);
    if (hasEmailChanged()) {
        if (checkEmailFormat(email.val())) {
            return true;
        } else {
            addErrorStyle(email, emailFormatError);
            return false;
        }
    }
}

function checkUsername() {
    const username = $(`#${NEW_USERNAME_INPUT_ID}`);
    const minLen = 4;
    removeErrorStyle(username);
    if (hasUsernameChanged()) {
        if (checkTextLen(username.val(), minLen)) {
            return true;
        } else {
            addErrorStyle(username, inputLenError);
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

function addErrorStyle(inputObj, errorText) {
    const inputObjParent = inputObj.parent();

    inputObjParent.addClass("has-error");
    inputObjParent.append(`<span class=\"help-block\">${errorText}</span>`);
}

function removeErrorStyle(inputObj) {
    const inputObjParent = inputObj.parent();

    inputObjParent.removeClass("has-error");
    inputObjParent.find("span").remove();
}
