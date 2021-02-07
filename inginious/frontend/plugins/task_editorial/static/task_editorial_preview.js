//Set the solution code and language on for CodeMirror

function setTaskSolutionCode(){

    $("#task_solution_container").show();
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

//Get and render the notebook file

function setSolutionNotebook(){
    $.get("/api/task_editorial/", {
        course_id: getCourseId(),
        task_id: getTaskId(),
        notebook_name: getNotebookName()
    }).done(function write(result) {
        const notebook_content = JSON.parse(result);
        const solution_notebook_container = $("#solution_notebook");
        render_notebook(notebook_content, solution_notebook_container);
    });
}

//Load solution editor/notebook after the solution modal

$("#task_solution_modal").on("shown.bs.modal", function () {
    if(!codeEditors["task_solution_code"]){
            setTaskSolutionCode();
    }
});

$("#task_solution_notebook_modal").on("shown.bs.modal", function () {
    setSolutionNotebook();
});
