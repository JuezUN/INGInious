function showHintAlert(message, status){
    let alert = $("#hint_modal_alert");
    if(status == "success"){
        alert.attr("class","alert alert-success");
    }
    if(status == "error"){
        alert.attr("class","alert alert-danger");
    }
    alert.text(message);
    alert.show();
    setTimeout(function(){
        hideHintAlert(alert);
    },10000);
}

function hideHintAlert(alert){
    alert.attr("class","");
    alert.text("");
}

/* Get the left hint content for the allowed hints*/
function loadHintsOnModal(){
    let to_show_hints = {};

    $.get("/api/hints_api/", {
        course_id: getCourseId(),
        task_id: getTaskId()
    }).done(function(result){
        to_show_hints = result.data;
        setHintsOnContainer(to_show_hints);
    })
}

/* Set message on the menu element for the hint*/
function setHintUnlockedStatus(index,hint){
    let hint_status = hint["allowed_to_see"];
    hint_option = $("#hint_menu_" + index).find("a");
    if(hint_status){
        hint_option.attr("class", "list-group-item list-group-item-success");
        hint_penalty = hint["penalty"];
        hint_option.find(".hint_penalty").text(hint_penalty);
    }else{
        hint_option.attr("class", "list-group-item list-group-item-success disabled");
        let message = hint_option.find("label").html();
        hint_option.find("label").html();
    }
}

/* Set the elements to show in the hint content */
function setHintsOnContainer(to_show_hints){
    let hint_status;
    $.each(to_show_hints, function(index, hint){
        hint_status = hint["allowed_to_see"];

        let hint_container = $("#hint_"+index);

        if(hint_status){

            new_hint_content = hint["content"];
            hint_container.find(".hint_content").html(new_hint_content);

            let applied_penalty = hint_container.find(".hint_applied_penalty");
            applied_penalty.show();
            applied_penalty.find("em").text(hint["penalty"]+"%");

        }else{
            if(!existsUnlockFormContent(index)){
                let new_hint = $("#hints_unlock_forms_list").clone().html();
                new_hint = new_hint.replace(/key/g, index);

                hint_container.find(".hint_content").append(new_hint);
                hint_container.find(".hint_content .hint_unlock_form").show();

                hint_penalty = hint["penalty"];

                /* Check if penalty exists to change the message */

                if(hint_penalty && hint_penalty != 0){
                    hint_container.find(".hint_content .hint_unlock_penalty b").html(hint_penalty + "%");
                }else{
                    let message = 'You can get this hint with no penalty.'
                    hint_container.find(".hint_content .hint_unlock_penalty").html(message);
                }
            }
        }

        setHintUnlockedStatus(index,hint);
    })
}

/* To check if the unlock form for the hint already exists */
function existsUnlockFormContent(index){
    let content = $("#hint_"+index).find(".hint_content .hint_unlock_form").html();
    return content;
}

/* Show or hide the hints by clicking the menu items*/
function changeHint(key){
    let hint_key = "hint_" + key;

    $("#hint_info").hide();
    $("#hint_container").show();

    $(".task_hints").each(function(index, element){
        if(element.id == hint_key){
            $("#" + element.id).show(500);
        }else{
            $("#" + element.id).hide();
        }
    })
}

/* Add the hint on the student allowed hints list*/
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
        showHintAlert(result.message,result.status);
        loadHintsOnModal();
        showHelp();
    })
}

function showHelp(){
    $("#hint_info").show(500);
    $("#hint_container").hide();
}

$(function(){
    loadHintsOnModal()
})
