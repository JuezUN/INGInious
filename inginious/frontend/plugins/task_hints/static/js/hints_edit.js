let update_hint_id = null;
let task_submission_mode = null;
let timer;

/* Show a message into an alert */
function displayAlert(alert_container_id, message, duration) {
    let alert = $("#" + alert_container_id);
    if (!alert.text()) {
        alert.text(message);
        alert.show();
        timer = setTimeout(function () {
            clearAlert(alert_container_id);
        }, duration);
    }
}

/* Clear and hide modal alert*/
function clearAlert(alert_id) {
    let alert = $("#" + alert_id);
    alert.fadeTo(100, 1).slideUp(250, () => {
        alert.hide();
        alert.text("");
        clearTimeout(timer);
    });
}

/* Load code editor for the hint content on modal */
function loadHintContentCodeEditor() {
    $("#hint_content_container").show();

    let hints_editor = codeEditors["task_hints_content"];
    hints_editor.refresh();
}

/* Save the new/modified hint in table */
$("#save_hint_button").on('click', function (event) {

    event.preventDefault();
    let hint = $.extend({
        "title": "",
        "penalty": 0.0,
        "content": ""
    }, {
        "title": $("#hint_title")[0].value,
        "penalty": parseFloat($("#hint_penalty")[0].value).toFixed(1),
        "content": $("#hint_content")[0].value
    });

    /* Check if the entries are allowed on the hint */

    const contentEmpty = hint["content"].match(/^\s*$/);
    let editAlert = "hint_edit_alert";

    if (!hint["title"] || contentEmpty) {
        const message = "You need to complete mandatory fields";
        displayAlert(editAlert, message, 10000);
        return;
    }
    if (isNaN(hint["penalty"])) {
        const message = "Hint penalty needs to be a number";
        displayAlert(editAlert, message, 10000);
        return;
    } else if (0 > hint["penalty"] || hint["penalty"] > 100) {
        const message = "Hint penalty must be between 0.0% and 100.0%";
        displayAlert(editAlert, message, 10000);
        return;
    }

    /* Update the table with the new/modified hint */
    let new_hint_index = $("#task_hints_table tbody tr").length;
    if (update_hint_id !== 0 && !update_hint_id) {
        addHintOnTable(hint, new_hint_index);
    } else {
        updateHintOnTable(hint, update_hint_id);
    }
    $("#hints_edit_modal").modal("hide");
});

/* Set the hint on table */
function addHintOnTable(new_hint, hint_id) {

    let new_hint_row_template = $("#hint_KEY").clone().html();
    let new_hint_id = "hint_" + hint_id;

    /* Replace "KEY" by the hint id */
    new_hint_row_template = new_hint_row_template.replace(/KEY/g, hint_id);
    new_hint_row_template = '<tr id=' + new_hint_id + '>' + new_hint_row_template + '</tr>';

    $("#task_hints_table tbody").append(new_hint_row_template);

    $("#hint_info_id_" + hint_id).val(new_hint.id);
    $("#hint_info_title_" + hint_id).val(new_hint.title);
    $("#hint_info_penalty_" + hint_id).val(new_hint.penalty);
    $("#hint_info_content_" + hint_id).text(new_hint.content);
}

/* Update the hint on table */

function updateHintOnTable(hint, hint_key) {

    $("#hint_info_title_" + hint_key).val(hint.title);
    $("#hint_info_penalty_" + hint_key).val(hint.penalty);
    $("#hint_info_content_" + hint_key).text(hint.content);

}

/* Get the saved hint in the table */
function loadSavedHintFromTable(hint_key) {
    return {
        "id": $("#hint_info_id_" + hint_key).val(),
        "title": $("#hint_info_title_" + hint_key).val(),
        "penalty": $("#hint_info_penalty_" + hint_key).val(),
        "content": $("#hint_info_content_" + hint_key).val()
    };
}

/* Set the hint data on modal to edit it */
function onEditHintClick(hint_key) {
    update_hint_id = hint_key;

    const hint = loadSavedHintFromTable(hint_key);

    $("#hint_title").val(hint["title"]);
    $("#hint_penalty").val(hint["penalty"]);
    codeEditors["task_hints_content"].getDoc().setValue(hint["content"]);
    $("#hints_edit_modal").modal("show");

}

/* Delete a hint from table */
function deleteHints(hint_key) {
    let table_hints = $("#task_hints_table tbody tr");
    const table_hints_number = table_hints.length;
    let to_update_hints = [];
    for (let i = 0; i < table_hints_number; i++) {
        if (i !== hint_key) {
            to_update_hints.push(loadSavedHintFromTable(i));
        }
    }
    $("#task_hints_table tbody").html("");
    $.each(to_update_hints, function (index, hint) {
        addHintOnTable(hint, index);
    })
}

function eraseModalInputs() {
    $("#hint_title").val("");
    $("#hint_penalty").val(0);
    codeEditors["task_hints_content"].getDoc().setValue("");
}

/**
 * Monkey-patch the function `studio_submit` from studio to save the task, including
 * task hints, to get the ids for new hints and set them in table
 */

const original_studio_submit = studio_submit;
studio_submit = () => {
    
    task_submssion_mode();
    original_studio_submit();
    getTaskHintsId();

    check_submission_mode_change();
};

function task_submssion_mode(){
    $.get("/api/hints_mode_api/", {
        course_id: getCourseId(),
        task_id: getTaskId()
    }).done(function (result) {
        task_submission_mode = result;
    })
}

function check_submission_mode_change(){
    $.post("/api/hints_mode_api/", {
        course_id: getCourseId(),
        task_id: getTaskId(),
        last_submission_mode: task_submission_mode
    })
}

function getTaskHintsId() {
    $.get("/api/edit_hints_api/", {
        course_id: getCourseId(),
        task_id: getTaskId()
    }).done(function (result) {
        const task_hints = result.data;
        setIdOnNewHints(task_hints);
    })
}

/* Set the ids for new hints, when task is saved */
function setIdOnNewHints(task_hints) {
    let hint_id;
    $.each(task_hints, function (index, hint) {
        hint_id = $("#hint_info_id_" + index).val();
        //Check if hint doesn't has it's respective id, and set them in table
        if (!hint_id) {
            $("#hint_info_id_" + index).val(hint.id);
        }
    })
}

$("#hints_edit_modal").on("shown.bs.modal", function () {
    loadHintContentCodeEditor();
});

$("#hints_edit_modal").on("hidden.bs.modal", function () {
    eraseModalInputs();
    update_hint_id = null;
    let editAlert = "hint_edit_alert";
    clearAlert(editAlert);
});
