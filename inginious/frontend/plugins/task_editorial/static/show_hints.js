function onAddHintClick(){

    let title = $("#hint_name")[0].value;
    let penalty = $("#hint_penalty")[0].value;
    let content = $("#hint_content")[0].value;

    let new_hint = {
        "title": title,
        "penalty": penalty,
        "content": content
    };

    createHintOnTable(new_hint);
}

function createHintOnTable(hint){

    let new_hint_row = $("#hint_id").clone();

    new_hint_row.attr("id",1);

    new_hint_row.find("hint_title").attr("value",hint.title);
    new_hint_row.find("hint_penalty").attr("value",hint.penalty);

    console.log(hint.title);

    new_hint_row.show();

    $("#task_hints_table").find('tbody').append(new_hint_row);

}

$(function(){
    $("#hint_id");
})

$("#hints_edit_modal").on("shown.bs.modal", function () {
    $("#hint_content_container").show();
});
