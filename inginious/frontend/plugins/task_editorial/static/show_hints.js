function onAddHintClick(){

    let title = $("#hint_name")[0].value;
    let penalty = $("#hint_penalty")[0].value;
    let content = $("#hint_content")[0].value;

    let new_hint = {
        "title": title,
        "penalty": penalty,
        "content": content
    };

    addHintInTable(new_hint);
}

function addHintInTable(hint){

    let new_hint_row = '<tr><td>' + hint["title"] + '</td>' +
                       '<td>' + hint["penalty"] + '</td>' +
                       '<td> <button type="button" class="btn btn-info">Edit</button> <button type="button" class="btn btn-danger">Delete</button></td></tr>';

    $("#task_hints_table tbody").append(new_hint_row);
}

$(function(){
    $("#hint_content_container").show();
})

$("#hints_edit_modal").on("shown.bs.modal", function () {
    $("#hint_content_container").show();
});
