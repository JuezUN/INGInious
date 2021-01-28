//Set the solution code and language on for CodeMirror

function setTaskSolutionCode(){

    const solution_code = ($("#task_solution_code")[0].attributes["value"].value);
    const mode = CodeMirror.findModeByName("python");

    const solution_preview_editor = codeEditors["task_solution_code"];
    solution_preview_editor.setValue(solution_code);
    solution_preview_editor.setOption("mode", mode.mime);
    solution_preview_editor.setOption("readOnly", true);
    CodeMirror.autoLoadMode(solution_preview_editor, mode["mode"]);

}

