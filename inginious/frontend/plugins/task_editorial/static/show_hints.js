function loadHintsOnModal(){

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

$(function(){

})
