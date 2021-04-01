function loadHintsOnModal(){
    let to_show_hints = {};

    $.get("/api/hints_api/", {
        course_id: getCourseId(),
        task_id: getTaskId()
    }).done(function(result){
        to_show_hints = result;
        console.log(to_show_hints);
        setHintsOnMenu(to_show_hints);
        setHintsOnContainer(to_show_hints);
    })
}

function setHintsOnMenu(to_show_hints){
    $.each(to_show_hints, function(index, element){
        let new_hint_menu_item = $("#hint_key_menu").clone().html();
        new_hint_menu_item = new_hint_menu_item.replace(/key/g, index);
        new_hint_menu_item = new_hint_menu_item.replace("hidden", "");

        new_hint_title = element["title"];
        new_hint_menu_item = new_hint_menu_item.replace("hint_tile",new_hint_title);

        $("#hints_list").append(new_hint_menu_item);
        setHintUnlockedStatus(index,element);
    })
}

function setHintUnlockedStatus(index,hint){
    let hint_status = hint["allowed_to_see"];
    if(hint_status){
        $("#hint_"+index+"_item").attr('class', 'list-group-item list-group-item-success');
    }
}

function setHintsOnContainer(to_show_hints){
    let hint_status;
    $.each(to_show_hints, function(index, element){
        hint_status = element["allowed_to_see"];

        let new_hint = $("#hint_container").clone().html();
        new_hint = new_hint.replace(/key/g, index);

        new_hint_title = element["title"];
        new_hint = new_hint.replace("hint_title",new_hint_title);

        if(hint_status){

            new_hint_content = element["content"];
            new_hint = new_hint.replace("hint_content", new_hint_content);

        }else{

            let new_hint = $("#hints_unlock_forms_list").clone().html();
            new_hint = new_hint.replace(/key/g, index);

            new_hint_penalty = element["penalty"];
            new_hint = new_hint.replace("hint_penalty", new_hint_penalty);

            $("#hints_unlock_forms_list").append(new_hint);
        }

        $("#hint_container").append(new_hint);
        setHintUnlockedStatus(index,element);
    })
}

function changeHint(hintKey){
    $(".task_hints").each(function(index, element){
        if(element.id.includes(hintKey)){
            $("#" + element.id).show(200);
        }else{
            $("#" + element.id).hide();
        }
    })
    $(".hint_unlock_form").each(function(index, element){
        if(element.id.includes(hintKey)){
            $("#" + element.id).show(200);
        }else{
            $("#" + element.id).hide();
        }
    })
}

function setHintAsAllowed(selected_hint_id){
    $.ajax({
        url: "/api/hints_api/",
        method: "POST",
        data: {
            course_id: getCourseId(),
            task_id: getTaskId(),
            hint_id: selected_hint_id
        }
    }).done(function(result){
        to_show_hints = result;

    })
}

$(function(){
    loadHintsOnModal()
})
