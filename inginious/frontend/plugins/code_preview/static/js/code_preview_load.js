function load_code_preview_to_codemirror() {
    if (location.href.indexOf("/course") > -1 && location.href.split('/').length == 6) {
        $.get('/api/code_preview/', {
            task_id: getTaskIdFromUrl(),
            course_id: getCourseIdFromUrl(),
            language: getInginiousLanguageForProblemId(getProblemId())
        }, function write(result) {
            if (result !== "") {
                const ks = Object.keys(codeEditors);
                ks.forEach(element => {
                    codeEditors[element].setValue(result);
                });
            }
        })
    }
}

jQuery(document).ready(function () {
    if (typeof getProblemId !== "undefined") {
        const language_elem = $('#' + getProblemId() + "\\/language");
        const last_call = language_elem.attr('onchange');
        language_elem.attr('onchange', last_call + ';load_code_preview_to_codemirror();');
        load_code_preview_to_codemirror();
    }
});