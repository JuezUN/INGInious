function showHintAlert(message, status) {
    let alert = $("#hint_modal_alert");
    if (status === "success") {
        alert.attr("class", "alert alert-success");
    }
    if (status === "error") {
        alert.attr("class", "alert alert-danger");
    }
    alert.text(message);
    alert.show();
    setTimeout(function () {
        hideHintAlert(alert);
    }, 10000);
}

function hideHintAlert(alert) {
    alert.attr("class", "");
    alert.text("");
}

/* Get the left hint content for the unlocked hints*/
function loadHintsOnModal() {
    let url = "/api/user_hints_api/";
    /* If task is lti, set the session id from task page in api url of the plugin.
       All api calls in task view that requires the user's session must add this validation.
    */
    if(is_lti()){
        url = "/" + ($("form#task").attr("action").split("/")[1]) + url; 
    } 
    $.get(url, {
        course_id: getCourseId(),
        task_id: getTaskId()
    }).done(function (result) {
        const hints_data = result.data;
        setHintsOnContainer(hints_data.hint_to_show);
        setTotalPenalty(hints_data.total_penalty);
    })
}

/* Set message on the menu element for the hint*/
function setHintUnlockedStatus(index, hint) {
    let hint_status = hint["unlocked"];
    const hint_option = $("#hint_menu_" + index).find("a");
    if (hint_status) {
        hint_option.attr("class", "list-group-item list-group-item-success");
        const hint_penalty = hint["penalty"];
        hint_option.find(".hint_penalty").text(hint_penalty);
    } else {
        hint_option.attr("class", "list-group-item list-group-item-success disabled");
    }
}

/* Set the elements to show in the hint content */
function setHintsOnContainer(to_show_hints) {
    let hint_status;
    $.each(to_show_hints, function (index, hint) {
        hint_status = hint["unlocked"];

        let hint_container = $("#hint_" + index);

        if (hint_status) {

            const new_hint_content = hint["content"];
            hint_container.find(".hint_content").html(new_hint_content);

            let applied_penalty = hint_container.find(".hint_applied_penalty");
            applied_penalty.show();
            applied_penalty.find("em").text(hint["penalty"] + "%");

        } else {
            if (!existsUnlockFormContent(index)) {
                let new_hint = $("#hints_unlock_forms_list").clone().html();
                new_hint = new_hint.replace(/key/g, index);

                hint_container.find(".hint_content").append(new_hint);
                hint_container.find(".hint_content .hint_unlock_form").show();

                const hint_penalty = hint["penalty"];

                /* Check if penalty exists to change the message */

                if (hint_penalty && hint_penalty !== 0) {
                    hint_container.find(".hint_content .hint_unlock_penalty b").html(hint_penalty + "%");
                } else {
                    let message = 'You can get this hint with no penalty.';
                    hint_container.find(".hint_content .hint_unlock_penalty").html(message);
                }
            }
        }

        setHintUnlockedStatus(index, hint);
    })
}

/* Set the hints total penalty of the user*/
function setTotalPenalty(user_total_penalty) {
    if (user_total_penalty) {
        $("#hints_total_penalty label").html(user_total_penalty + "%")
    }
}

/* To check if the unlock form for the hint already exists */
function existsUnlockFormContent(index) {
    return $("#hint_" + index).find(".hint_content .hint_unlock_form").html();
}

/* Show or hide the hints by clicking the menu items*/
function changeHint(key) {
    let hint_key = "hint_" + key;

    $("#hint_info").hide();
    $("#hint_container").show();

    $(".task_hints").each(function (index, element) {
        if (element.id === hint_key) {
            $("#" + element.id).show(500);
        } else {
            $("#" + element.id).hide();
        }
    })
}

/* Add the hint on the student unlocked hints list*/
function unlockNewHint(selected_hint_id) {
    let url = "/api/user_hints_api/";

    /* If task is lti, set the session id from task page in api url of the plugin.
       All api calls in task view that requires the user's session must add this validation.
    */
    if(is_lti()){
        url = "/" + ($("form#task").attr("action").split("/")[1]) + url;
    }
    $.ajax({
        url: url,
        method: "POST",
        data: {
            course_id: getCourseId(),
            task_id: getTaskId(),
            hint_id: selected_hint_id
        }
    }).done(function (result) {
        showHintAlert(result.message, result.status);
        updateHintsModalData();
        sendUseTaskHintsAnalytics();
    })
}

/* Send analytics when a user unlock a hint */
function sendUseTaskHintsAnalytics() {
    let url = "/api/analytics/";
    //Verify if is a lti task, and set the actual session id from task page (Do that for all analytics calls in task view)
    if(is_lti()){
        url = "/" + ($("form#task").attr("action").split("/")[1]) + url;
    }
    $.post(url, {
        service: {
            key: "task_hints_unlock",
            name: "Task hints - Unlocked by students"
        },
        course_id: getCourseId()
    })
}

function showHelp() {
    $("#hint_info").show(500);
    $("#hint_container").hide();
}

function updateHintsModalData() {
    $("#hint_container").hide();
    loadHintsOnModal();
    $("#hint_container").show(500);
}
