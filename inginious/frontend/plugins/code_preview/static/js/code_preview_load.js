function load_code_preview_to_codemirror(){
    $.get('/api/code_preview/', {
        task_id: getTaskIdFromUrl(),
        course_id: getCourseIdFromUrl(),
        language: getInginiousLanguageForProblemId(getProblemId())
    }, function write(result) {
        ks = Object.keys(codeEditors);
        ks.forEach(element => {
            codeEditors[element].setValue(result);
        });
    })
}

jQuery(document).ready(function () {
        let last_call = $('#' + getProblemId() + "\\/language").attr('onchange');
        $('#' + getProblemId() + "\\/language").attr('onchange', last_call + ';load_code_preview_to_codemirror();')
        load_code_preview_to_codemirror();
});