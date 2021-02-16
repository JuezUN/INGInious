let solution_language = "";
let notebook_name = "";

//Remove options from selector to avoid duplication
function deleteLanguageSelectOptions(){
    $(".solution_language_select_option").remove();
}

//Add a new option for each language for multilang, HDL and Data Science problems
function addTaskLanguages() {

    deleteLanguageSelectOptions();

    const solutionLanguageSelect = $("#solution_code_language");
    const languagesList = $(".checkbox_language");
    const languagesListSize = languagesList.length;

    for(let i = 0; i < languagesListSize; i++){
        if(languagesList[i].checked){
           const newOption = `<option class="solution_language_select_option" value="${languagesList[i].value}">${getLanguages(languagesList[i].value)}</option>`;
           solutionLanguageSelect.append(newOption);
        }
    }
}

//Set the last language saved on task
function setLastTaskSolutionCodeLanguage(){

    const solutionCodeLanguage = solution_language;

    if(solutionCodeLanguage){

        //Check if the last saved language is in the available languages
        let isInOptions = false;
        $("#solution_code_language option").each(function() {
            if(this.value.localeCompare(solutionCodeLanguage) == 0){
                isInOptions = true;
            };
        });

        const solutionLanguageSelect = $("#solution_code_language");
        if(isInOptions){
            solutionLanguageSelect[0].value = solutionCodeLanguage;
        }else{
            solutionLanguageSelect[0].value = "0";
        }
    }
}

//From the selected option, change the language of the code editor
function setSolutionCodeLanguage(){

    const solutionLanguageKey = $("#solution_code_language")[0].value;
    if(solutionLanguageKey != 0){
        const solutionLanguage = convertInginiousLanguageToCodemirror(solutionLanguageKey);

        const solutionEditor = codeEditors["solution_code"];
        const mode = CodeMirror.findModeByName(solutionLanguage);
        solutionEditor.setOption("mode", mode.mime);

        CodeMirror.autoLoadMode(solutionEditor, mode["mode"]);
    }else{
        const solutionEditor = codeEditors["solution_code"];
        solutionEditor.setOption("mode", "text/plain");
    }
}

//Remove options from selector to avoid duplication
function deleteNotebookNameSelectOptions(){
    $(".solution_notebook_select_option").remove();
}

//Get all the task files and put their names on the notebook solution selector
function addTaskFiles(){

     deleteNotebookNameSelectOptions();
     const solutionLanguageSelect = $("#solution_code_notebook");
     const solutionNotebookName = notebook_name;

     $.get("/api/grader_generator/test_file_api", {
        course_id: getCourseId(),
        task_id: getTaskId(),
     }, function (files) {
        $.each(files, function (index, file) {
            if(file.complete_name.includes('ipynb')){
                solutionLanguageSelect.append(`<option class="solution_notebook_select_option" value="${file.complete_name}">${file.complete_name}</option>`);

                //Set the last notebook name saved on task
                if(file.complete_name.localeCompare(solutionNotebookName) == 0){
                    $("#solution_code_notebook")[0].value = solutionNotebookName;
                };
            }
        });
     });
}

//Get the solution code and language from previous task save
function loadLastSolutionConfiguration(){
    addTaskLanguages();
    setLastTaskSolutionCodeLanguage();
    setSolutionCodeLanguage();
}

function setTaskSolutionForm(){

    const taskEnvironment = $("#environment").val();
    if(["multiple_languages" , "Data Science" , "HDL"].includes(taskEnvironment)){
        $("#multiple_languages_task_solution").show();
        $("#notebook_task_solution").hide();
    }
    else if (["Notebook"].includes(taskEnvironment)){
        $("#notebook_task_solution").show();
        $("#multiple_languages_task_solution").hide();
    }
}

//Update editorial elements when click on editorial tab
$("a[data-toggle='tab'][href='#tab_editorial']").on("show.bs.tab", function (e) {
    setTaskSolutionForm();
    if(["multiple_languages" , "Data Science" , "HDL"].includes($("#environment").val())){
       loadLastSolutionConfiguration();
    }else if (["Notebook"].includes($("#environment").val())){
       addTaskFiles();
    }
});

$("#solution_code_language").on("change", function (e) {
    solution_language = $("#solution_code_language")[0].value;
});

$("#solution_code_notebook").on("change", function (e) {
    notebook_name = $("#solution_code_notebook")[0].value;
});

jQuery(document).ready(function () {
    setTaskSolutionForm();
    if(["multiple_languages" , "Data Science" , "HDL"].includes($("#environment").val())){
       solution_language = getTaskSolutionCodeLanguage();
       loadLastSolutionConfiguration();
    }else if (["Notebook"].includes($("#environment").val())){
       notebook_name = getTaskSolutionNotebook();
       addTaskFiles();
    }
});
