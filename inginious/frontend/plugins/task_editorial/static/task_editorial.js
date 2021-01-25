function addTaskLanguages() {

    const tutorial_language_select = $("#task_solution_language");

    const languages_list = $(".checkbox_language");
    const languages_list_size = languages_list.length;

    for(let i = 0; i < languages_list_size; i++){
        if(languages_list[i].checked){
           new_option = `<option value="${languages_list[i].value}">${getLanguagesCodes(languages_list[i].value)}</option>`;
           tutorial_language_select.append(new_option);
        }
    }
}

function setSolutionCodeLanguage(){

    const solution_language_key = $("#task_solution_language")[0].value;
    const solution_language = convertInginiousLanguageToCodemirror(solution_language_key);

    const solution_editor = codeEditors["solution_code"];
    const mode = CodeMirror.findModeByName(solution_language);
    solution_editor.setOption("mode", mode.mime);

    CodeMirror.autoLoadMode(solution_editor, mode["mode"]);

}

jQuery(document).ready(function () {
    addTaskLanguages();
});
