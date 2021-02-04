//Remove options from selector to avoid duplication
function deleteLanguageSelectOptions(){
    $(".solution_language_select_option").remove();
}

//Add a new option for each language for multilang, HDL and Data Science problems
function addTaskLanguages() {

    deleteLanguageSelectOptions();

    const solution_language_select = $("#solution_code_language");
    const languages_list = $(".checkbox_language");
    const languages_list_size = languages_list.length;

    for(let i = 0; i < languages_list_size; i++){
        if(languages_list[i].checked){
           new_option = `<option class="solution_language_select_option" value="${languages_list[i].value}">${getLanguages(languages_list[i].value)}</option>`;
           solution_language_select.append(new_option);
        }
    }
};
//Set the last language saved on task
function setLastTaskSolutionCodeLanguage(){

    const solution_code_language = getTaskSolutionCodeLanguage();

    if(solution_code_language){

        //Check if the last saved language is in the available languages
        let isInOptions = false;
        $("#solution_code_language option").each(function() {
            if(this.value.localeCompare(solution_code_language) == 0){
                isInOptions = true;
            };
        });

        const solution_language_select = $("#solution_code_language");
        if(isInOptions){
            solution_language_select[0].value = solution_code_language;
        }else{
            solution_language_select[0].value = "0";
        }
    }
};

//From the selected option, change the language of the code editor
function setSolutionCodeLanguage(){

    const solution_language_key = $("#solution_code_language")[0].value;
    if(solution_language_key != 0){
        const solution_language = convertInginiousLanguageToCodemirror(solution_language_key);

        const solution_editor = codeEditors["solution_code"];
        const mode = CodeMirror.findModeByName(solution_language);
        solution_editor.setOption("mode", mode.mime);

        CodeMirror.autoLoadMode(solution_editor, mode["mode"]);
    }
};

//Get all the task files and put their names on the notebook solution selector

function addTaskFiles(){

     $(".solution_notebook_select_option").remove();
     const solution_language_select = $("#solution_code_notebook");

     $.get("/api/grader_generator/test_file_api", {
        course_id: getCourseId(),
        task_id: getTaskId(),
     }, function (files) {
        $.each(files, function (index, file) {
            solution_language_select.append(`<option class="solution_notebook_select_option" value="${file.complete_name}">${file.complete_name}</option>`);
            console.log(file.complete_name);
        })
     });
}

//Get the solution code and language from previous task save
function loadLastSolutionConfiguration(){
    addTaskLanguages();
    setLastTaskSolutionCodeLanguage();
    setSolutionCodeLanguage();
}

//Update editorial elements when click on editorial tab
$("a[data-toggle='tab'][href='#tab_editorial']").on("show.bs.tab", function (e) {
    if(["multiple_languages" , "Data Science" , "HDL"].includes(getTaskEnvironment())){
       loadLastSolutionConfiguration();
    }else if (["Notebook"].includes(getTaskEnvironment())){
        addTaskFiles();
    }
});

jQuery(document).ready(function () {
    if(["multiple_languages" , "Data Science" , "HDL"].includes(getTaskEnvironment())){
       loadLastSolutionConfiguration();
    }else if (["Notebook"].includes(getTaskEnvironment())){
        addTaskFiles();
    }
});
