const USER_LIST_DIV_ID = "listOfUsers";
const USER_TABLE_ID = "userList";
const FIELD_OPTION_ID = "fieldOption";
const SEARCH_BTN_ID = "searchBtn";

function addSearchBtnListener() {
    $(`#${SEARCH_BTN_ID}`).on("click", function () {
        if (checkSearchInput()) {
            const fieldOption = $(`#${FIELD_OPTION_ID}`).val();
            const usernameOrEmail = getSearchParameter();
            $.get("/api/find_user", {
                user: usernameOrEmail,
                field: fieldOption
            }, function (data) {
                _updateUserTable(data);
                cleanNotifications();
            });
        } else {
            new MessageBox(NOTIFICATIONS_ID, inputGeneralError, "danger", false);
        }

    });
}

function configUserTable() {
    cleanUserTable();
    hideUserTableDiv();
}

function showUserTableDiv() {
    $(`#${USER_LIST_DIV_ID}`).show();
}

function hideUserTableDiv() {
    $(`#${USER_LIST_DIV_ID}`).hide();
}

function _updateUserTable(data) {
    const userList = data["users"];
    configUserTable();
    if (userList.length) {
        _appendUsersToTable(userList);
    } else {
        _appendNoUserMessage();
    }
    showUserTableDiv();
}

function cleanUserTable() {
    $(`#${USER_TABLE_ID}`).empty();
}

function _appendUsersToTable(userList) {
    const table = $(`#${USER_TABLE_ID}`);
    $.each(userList, (_, user) => {
        table.append(_createUserItem(user));
    })
}

function _createUserItem(userData) {
    const username = userData["username"];
    const email = userData["email"];
    const name = userData["realname"];
    return `<tr class="itemSelection" onclick='requestUser(\"${username}\")'><td>${username}</td><td>${email}</td><td>${name}</td></tr>`;
}

function _appendNoUserMessage() {
    const noUserMessage = `<tr><td colspan="3" class="text-center"><h4>${noUser}</h4></td></tr>`;
    $(`#${USER_TABLE_ID}`).append(noUserMessage);
}

function checkSearchInput() {
    const usernameOrEmail = $(`#${USERNAME_OR_EMAIL_INPUT_ID}`);
    const minLen = 4;
    removeErrorStyle(usernameOrEmail);
    if (checkTextLen(usernameOrEmail.val(), minLen)) {
        return true;
    } else {
        addErrorStyle(usernameOrEmail, inputLenError);
        return false;
    }
}

function getSearchParameter() {
    return $(`#${USERNAME_OR_EMAIL_INPUT_ID}`).val();

}