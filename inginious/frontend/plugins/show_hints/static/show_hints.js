function loadHintsOnModal(){
    $.get("/api/hints_api/", {
        course_id: getCourseId(),
        task_id: getTaskId(),
    }).done(function(result){
    })
}

function changeHint(hintKey){
    let key;
    $(".hintte").each(function(index, element){
        if(element.id.includes(hintKey)){
            $("#" + element.id).show(200);
        }else{
            $("#" + element.id).hide();
        }
    })
}

