function loadHintsOnModal(){
    let to_show_hints = {};

    $.get("/api/hints_api/", {
        course_id: getCourseId(),
        task_id: getTaskId()
    }).done(function(result){
        to_show_hints = result;
        //setHintsOnMenu(to_show_hints);
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
        $("#hint_menu_" + index).find("a").attr('class', 'list-group-item list-group-item-success');
    }
}

function setHintsOnContainer(to_show_hints){
    let hint_status;
    $.each(to_show_hints, function(index, hint){
        hint_status = hint["allowed_to_see"];

        let hint_container = $("#hint_"+index);

        console.log(hint_status);

        if(hint_status){

            new_hint_content = hint["content"];
            hint_container.find(".hint_content").html(new_hint_content);

        }else{

            let new_hint = $("#hints_unlock_forms_list").clone().html();
            new_hint = new_hint.replace(/key/g, index);

            hint_container.find(".hint_content").append(new_hint);
            hint_container.find(".hint_content .hint_unlock_form").show();

            new_hint_penalty = hint["penalty"];
            hint_container.find(".hint_content .hint_unlock_form .hint_penalty").html(new_hint_penalty + "%");
        }

        setHintUnlockedStatus(index,hint);
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
