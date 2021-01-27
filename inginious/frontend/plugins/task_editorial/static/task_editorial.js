//Remove options from selector to avoid duplication
function deleteLanguageSelectOptions(){
    $(".tutorial_language_select_option").remove();
}

//Add a new option for each language for multilang and HDL problems
function addTaskLanguages() {

    deleteLanguageSelectOptions();

    const tutorial_language_select = $("#solution_code_language");
    const languages_list = $(".checkbox_language");
    const languages_list_size = languages_list.length;

    for(let i = 0; i < languages_list_size; i++){
        if(languages_list[i].checked){
           new_option = `<option class="tutorial_language_select_option" value="${languages_list[i].value}">${getLanguages(languages_list[i].value)}</option>`;
           tutorial_language_select.append(new_option);
        }
    }
};

function setLastTaskSolutionCodeLanguage(){

    const solution_code_language = getTaskSolutionCodeLanguage();
    const tutorial_language_select = $("#solution_code_language");
    tutorial_language_select[0].value = solution_code_language;

};

//From the selected option, change the language of the code editor
function setSolutionCodeLanguage(){

    const solution_language_key = $("#solution_code_language")[0].value;
    const solution_language = convertInginiousLanguageToCodemirror(solution_language_key);

    const solution_editor = codeEditors["solution_code"];
    const mode = CodeMirror.findModeByName(solution_language);
    solution_editor.setOption("mode", mode.mime);

    CodeMirror.autoLoadMode(solution_editor, mode["mode"]);
};

jQuery(document).ready(function () {
    if (["HDL", "multiple_languages"].includes(getTaskEnvironment())){
        addTaskLanguages();
    }
    setTaskSolutionCodeLanguage();
});
