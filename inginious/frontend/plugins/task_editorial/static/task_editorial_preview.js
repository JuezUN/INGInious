//Set the solution code and language on for CodeMirror
function setTaskSolutionCode(){

    $("#task_solution_container").show();
    const solutionCode = $("#task_solution_code")[0].attributes["value"].value;
    const solutionCodeLanguage = convertInginiousLanguageToCodemirror(getSolutionLanguage());
    if(solutionCodeLanguage){
        const solutionPreviewEditor = registerCodeEditor($("#task_solution_code")[0], solutionCodeLanguage, 10);
        solutionPreviewEditor.setValue(solutionCode);
        solutionPreviewEditor.setOption("readOnly", "nocursor");
    }else{
        const solutionPreviewEditor = registerCodeEditor($("#task_solution_code")[0], 'text', 10);
        solutionPreviewEditor.setValue(solutionCode);
        solutionPreviewEditor.setOption("readOnly", "nocursor");
    }
    sendAnalyticsTaskSolution();
}

//Get and render the notebook file
function setSolutionNotebook(){
    $.get("/api/task_editorial/", {
        course_id: getCourseId(),
        task_id: getTaskId(),
        notebook_name: getNotebookName()
    }).done(function write(result) {
        const notebookContent = JSON.parse(result);
        const solutionNotebookContainer = $("#solution_notebook");
        render_notebook(notebookContent, solutionNotebookContainer);
        sendAnalyticsTaskSolution();
    });
}

//Send analytics when a user see the task editorial - tutorial just one time by load data in modal
function sendAnalyticsTaskTutorial(){
    let url = "/api/analytics/";
    if(is_lti()){
        url = "/" + ($("form#task").attr("action").split("/")[1]) + url; 
    }
    $.post(url, {
        service: {
            key: "task_tutorial",
            name: "Task editorial - Tutorial"
        },
        course_id: getCourseId()
    })
}

//Send analytics when a user see the task editorial - solution everytime he enter the task for the first time
function sendAnalyticsTaskSolution(){
    let url = "/api/analytics/";
    if(is_lti()){
        url = "/" + ($("form#task").attr("action").split("/")[1]) + url;
    }
    $.post(url, {
        service: {
            key: "task_solution",
            name: "Task editorial - Solution"
        },
        course_id: getCourseId()
    })
}

$("#task_tutorial_modal").one("shown.bs.modal", function () {
    sendAnalyticsTaskTutorial();
});

//Load solution editor/notebook after the solution modal

$("#task_solution_modal").one("shown.bs.modal", function () {
    if(!codeEditors["task_solution_code"]){
            setTaskSolutionCode();
    }
});

$("#task_solution_notebook_modal").one("shown.bs.modal", function () {
    setSolutionNotebook();
});
