

function getLanguages(){
    const languagesList = "$task_data.get('problems',{})";
    return languagesList;
}

function addTaskLanguages() {

    const tutorial_language_select = $("#task_tutorial_language");

    const languages_list = $(".checkbox_language");
    const languages_list_size = languages_list.length;

    for(let i = 0; i < languages_list_size; i++){
        if(languages_list[i].checked){
           new_option = `<option value="${languages_list[i].value}">${getAllLanguages(languages_list[i].value)}</option>`;
           tutorial_language_select.append(new_option);
        }
    }
}

jQuery(document).ready(function () {
    addTaskLanguages();
});
