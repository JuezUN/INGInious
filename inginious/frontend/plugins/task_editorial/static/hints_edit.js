function onAddHintClick(){

    let title = $("#hint_name")[0].value;
    let penalty = $("#hint_penalty")[0].value;
    let content = $("#hint_content")[0].value;

    let new_hint_index = $("#task_hints_table").find('tbody tr').length;

    addHintOnTable({
        "title": title,
        "penalty": penalty,
        "content": content
    }, new_hint_index);

    $("#hints_edit_modal").modal('hide');

}

function addHintOnTable(new_hint, index){

    new_hint = $.extend({
        "penalty": 0,
    }, new_hint)

    var new_hint_row_template = $("#hint_id").clone().html();
    let new_hint_id = "hint_" + index;

    new_hint_row_template = new_hint_row_template.replace(/hint_id/g, index);
    new_hint_row_template = '<tr id='+new_hint_id+'>'+ new_hint_row_template +'</tr>';

    $("#task_hints_table").find('tbody').append(new_hint_row_template);
    $("#"+new_hint_id).find("#hint_info_title input").val(new_hint.title);
    $("#"+new_hint_id).find("#hint_info_penalty input").val(new_hint.penalty);
    $("#"+new_hint_id).find("#hint_info_content input").val(new_hint.content);

}

function loadSavedHintsOnTable(){

    let hints = getTaskHints();
    let hints_table = $("#task_hints_table");

}

function editHints(index){

    console.log(index);

}

function deleteHints(index){

}

function getHintKey(){

}

$(function(){
    $("#hint_id");
})

$("#hints_edit_modal").on("shown.bs.modal", function () {
    $("#hint_content_container").show();
});
