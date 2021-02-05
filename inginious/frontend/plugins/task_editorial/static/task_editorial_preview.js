//Set the solution code and language on for CodeMirror

function setTaskSolutionCode(){

    $("#solution_test").show();
    const solution_code = $("#task_solution_code")[0].attributes["value"].value;
    const solution_code_language = convertInginiousLanguageToCodemirror(getSolutionLanguage());
    if(solution_code_language){
        const solution_preview_editor = registerCodeEditor($("#task_solution_code")[0], solution_code_language, 10);
        solution_preview_editor.setValue(solution_code);
        solution_preview_editor.setOption("readOnly", "nocursor");
    }else{
        const solution_preview_editor = registerCodeEditor($("#task_solution_code")[0], 'text', 10);
        solution_preview_editor.setValue(solution_code);
        solution_preview_editor.setOption("readOnly", "nocursor");
    }
}

//Load solution editor after the solution modal

$("#task_solution_modal").on("shown.bs.modal", function () {
    if(!codeEditors["task_solution_code"]){
        setTaskSolutionCode();
    }
});


