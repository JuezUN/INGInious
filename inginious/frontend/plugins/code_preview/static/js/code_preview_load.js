jQuery(document).ready(function () {
        function load_code_preview_to_codemirror(){
            $.get('/api/code_preview/', {
                task_id: getTaskIdFromUrl(),
                course_id: getCourseIdFromUrl()
            }, function write(result) {
                ks = Object.keys(codeEditors);
                ks.forEach(element => {
                    codeEditors[element].setValue(result);
                });
            })
        }
        load_code_preview_to_codemirror();
});