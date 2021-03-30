var update_hint_id = null;

/*Show a message into an alert*/
function displayAlert(message, duration){
    let alert = $("#hint_edit_alert");
    alert.text(message);
    alert.show();
    setTimeout(function(){
        alert.hide();
    }, duration);
}

/*Load code editor for the hint content on modal*/
function loadHintContentCodeEditor(){
    $("#hint_content_container").show();

    let hints_editor = codeEditors["task_hints_content"];
    hints_editor.refresh();
}

function onAddHintClick(){

    let hint = $.extend({
        "title" : "",
        "penalty" : 0.0,
        "content" : ""
    },{
        "title" : $("#hint_title")[0].value,
        "penalty" : parseFloat($("#hint_penalty")[0].value),
        "content" : $("#hint_content")[0].value
    });

    /*Check if the entries are allowed on the hint*/

    if(!hint["title"] || !hint["content"]){
        const message = "You need to complete mandatory fields";
        displayAlert(message, 10000);
        return ;
    }
    if(isNaN(hint["penalty"])){
        const message = "Hint penalty needs to be a number";
        displayAlert(message, 10000);
        return ;
    } else if (0 > hint["penalty"] || hint["penalty"] > 100){
        const message = "Hint penalty must be between 0.0% and 100.0%";
        displayAlert(message, 10000);
        return ;
    }

    /*Update the table with the new/modified hint*/

    let new_hint_index = $("#task_hints_table tbody tr").length;

    if(!update_hint_id){
        addHintOnTable(hint, new_hint_index);
    }else{
        updateHintOnTable(hint, update_hint_id);
        update_hint_id = null;
    }
    $("#hints_edit_modal").modal("hide");
}

/*Set the hint on table*/
function addHintOnTable(new_hint, id){

    var new_hint_row_template = $("#hint_hid").clone().html();
    let new_hint_id = "hint_" + id;

  /*Replace "hid" by the hint id*/
    new_hint_row_template = new_hint_row_template.replace(/hid/g, id);
    new_hint_row_template = '<tr id='+new_hint_id+'>'+ new_hint_row_template +'</tr>';

    $("#task_hints_table tbody").append(new_hint_row_template);
    $("#hint_info_title input").val(new_hint.title);
    $("#hint_info_penalty input").val(new_hint.penalty);
    $("#hint_info_content input").val(new_hint.content);
}

/*Update the hint on table*/

function updateHintOnTable(hint, hintKey){

     let hint_id = "hint_" + hintKey;

     $("#hint_info_title_"+hintKey).find("input").val(hint.title);
     $("#hint_info_penalty_"+hintKey).find("input").val(hint.penalty);
     $("#hint_info_content_"+hintKey).find("input").val(hint.content);

}

/*Get the saved hint in the table*/
function loadSavedHintFromTable(hintKey){

    const hint = {
        "title": $("#hint_info_title_"+hintKey).find("input").val(),
        "penalty": $("#hint_info_penalty_"+hintKey).find("input").val(),
        "content": $("#hint_info_content_"+hintKey).find("input").val()
    }

    return hint;
}

function onEditHintClick(hintKey){

    update_hint_id = hintKey;

    const hint = loadSavedHintFromTable(hintKey);

    $("#hint_title").val(hint["title"]);
    $("#hint_penalty").val(hint["penalty"]);
    codeEditors["task_hints_content"].getDoc().setValue(hint["content"]);
    $("#hints_edit_modal").modal("show");

}

function deleteHints(hintKey){
    let hints = $("#task_hints_table tbody tr");
    let hint_row = null;
    $.each(hints,function(index, hint){
        if(hintKey == index){
            hint_row = $("#hint_"+index)[0];
        };
    });
    if(hint_row){
        hint_row.remove();
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
});
