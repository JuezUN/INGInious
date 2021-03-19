function onAddHintClick(){

    var title = $("#hint_name")[0].value;
    var penalty = $("#hint_penalty")[0].value;
    var content = $("#hint_content")[0].value;

    var new_hint = {
        "title": title,
        "penalty": penalty,
        "content": content
    };

    createHintOnTable(new_hint);

}

function createHintOnTable(hint){

    let new_hint_index = 10;
    let new_hint_id = "hint_" + new_hint_index;

    var new_hint_row = $("#hint_id").clone().html();

    new_hint_row = new_hint_row.replace(/hint_id/g, new_hint_index);

    new_hint_row = '<tr id='+new_hint_id+'>'+ new_hint_row +'</tr>';

    $("#task_hints_table").find('tbody').append(new_hint_row);

    $("#"+new_hint_id).find("#hint_info_title input").val(456);

    $("#"+new_hint_id).find("#hint_info_penalty input").val(123);

    $("#hints_edit_modal").modal('hide');
}

$(function(){
    $("#hint_id");
})

$("#hints_edit_modal").on("shown.bs.modal", function () {
    $("#hint_content_container").show();
});
