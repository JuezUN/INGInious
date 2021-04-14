var update_hint_id = null;

/* Show a message into an alert */
function displayAlert(alert_container_id, message, duration){
    alert = $("#"+alert_container_id);
    alert.text(message);
    alert.show();
    setTimeout(function(){
        clearAlert(alert_container_id);
    }, duration);
}

/* Clear and hide modal alert*/
function clearAlert(alert_id){
    let alert = $("#"+alert_id);
    alert.fadeTo(100, 1).slideUp(250, () => {
        alert.slideUp(250);
        alert.text("");
    });
}

/* Load code editor for the hint content on modal */
function loadHintContentCodeEditor(){
    $("#hint_content_container").show();

    let hints_editor = codeEditors["task_hints_content"];
    hints_editor.refresh();
}

function onSaveHintClick(){

    let hint = $.extend({
        "title" : "",
        "penalty" : 0.0,
        "content" : ""
    },{
        "title" : $("#hint_title")[0].value,
        "penalty" : parseFloat($("#hint_penalty")[0].value),
        "content" : $("#hint_content")[0].value
    });

    /* Check if the entries are allowed on the hint */

    let contentBlankEntry = hint["content"].match(/^\s*$/)

    if(!hint["title"] || contentBlankEntry){
        const message = "You need to complete mandatory fields";
        let editAlert = "hint_edit_alert";
        displayAlert(editAlert, message, 10000);
        return ;
    }
    if(isNaN(hint["penalty"])){
        const message = "Hint penalty needs to be a number";
        let editAlert = "hint_edit_alert";
        displayAlert(editAlert, message, 10000);
        return ;
    } else if (0 > hint["penalty"] || hint["penalty"] > 100){
        const message = "Hint penalty must be between 0.0% and 100.0%";
        let editAlert = "hint_edit_alert";
        displayAlert(editAlert, message, 10000);
        return ;
    }

    /* Update the table with the new/modified hint */

    let new_hint_index = $("#task_hints_table tbody tr").length;

    if(update_hint_id && update_hint_id !== 0){
        updateHintOnTable(hint, update_hint_id);
    }
    $("#hints_edit_modal").modal("hide");
}

/* Set the hint on table */
function addHintOnTable(){

  let hint_id = $("#hint_id").val();
  let new_hint_id = "hint_"+hint_id;

  /* Check by alphanumeric id */
  if(!hint_id.match(/[a-zA-Z0-9]+$/)){
    const message = "The hint ID only should contains alphanumeric characters.";
    let tabHintAlert = "hint_tab_alert";
    displayAlert(tabHintAlert, message, 10000);
    return;
  }
  if(checkIDExists(hint_id)){
    const message = "The hint ID already exist for another hint";
    let tabHintAlert = "hint_tab_alert";
    displayAlert(tabHintAlert, message, 10000);
    return;
  }

  var new_hint_row_template = $("#hint_HID").clone().html();

  /* Replace "HID" by the hint id */
  new_hint_row_template = new_hint_row_template.replace(/HID/g, hint_id);
  new_hint_row_template = '<tr id='+new_hint_id+'>'+ new_hint_row_template +'</tr>';

  $("#task_hints_table tbody").append(new_hint_row_template);
}

/* Check if id already exists*/
function checkIDExists(key){
    let hint_key = "hint_"+key;
    let table_hints = $("#task_hints_table tbody tr");
    const table_hints_number = table_hints.length;
    for(let i = 0; i < table_hints_number; i++){
        if(hint_key == table_hints[i].id){
            return true;
        }
    }
    return false;
}

/* Update the hint on table */

function updateHintOnTable(hint, hint_key){

     let hint_id = "hint_" + hint_key;

     $("#hint_info_title_"+hint_key).val(hint.title);
     $("#hint_info_penalty_"+hint_key).val(hint.penalty);
     $("#hint_info_content_"+hint_key).text(hint.content);

}

/* Get the saved hint in the table */
function loadSavedHintFromTable(hint_key){

    const hint = {
        "title": $("#hint_info_title_"+hint_key).val(),
        "penalty": $("#hint_info_penalty_"+hint_key).val(),
        "content": $("#hint_info_content_"+hint_key).val()
    }

    return hint;
}

/* Set the hint data on modal to edit it */
function onEditHintClick(hint_key){

    update_hint_id = hint_key;

    const hint = loadSavedHintFromTable(hint_key);

    $("#hint_title").val(hint["title"]);
    $("#hint_penalty").val(hint["penalty"]);
    codeEditors["task_hints_content"].getDoc().setValue(hint["content"]);
    $("#hints_edit_modal").modal("show");

}

/* Delete a hint from table */
function deleteHints(key){
    if(checkIDExists(key)){
        $("#hint_" + key).remove();
    }
}

function eraseModalInputs(){
    $("#hint_title").val("");
    $("#hint_penalty").val(0);
    codeEditors["task_hints_content"].getDoc().setValue("");
};

$("#hints_edit_modal").on("shown.bs.modal", function () {
    loadHintContentCodeEditor();
});

$("#hints_edit_modal").on("hidden.bs.modal", function () {
    eraseModalInputs();
    update_hint_id = null;
    let editAlert = "hint_edit_alert";
    clearAlert(editAlert);
});
