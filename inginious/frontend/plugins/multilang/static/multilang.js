function load_input_code_multiple_languages(submissionid, key, input)
{
    load_input_code(submissionid, key, input);
    setDropDownWithTheRightLanguage(key, input[key + "/language"]);
    changeSubmissionLanguage(key);
}

function setDropDownWithTheRightLanguage(key, language)
{
    var dropDown = document.getElementById(key + '/language');
    dropDown.value = language;
}

function changeSubmissionLanguage(key){
    var language = getLanguageForProblemId(key);
    var editor = codeEditors[key];
    var mode = CodeMirror.findModeByName(language);
    editor.setOption("mode", mode.mime);
    CodeMirror.autoLoadMode(editor, mode["mode"]);
}

function getLanguageForProblemId(key){
    var dropDown = document.getElementById(key + '/language');
    if(dropDown == null)
        return "plain";

    var inginiousLanguage = dropDown.options[dropDown.selectedIndex].value;
    return convertInginiousLanguageToCodemirror(inginiousLanguage);
}

function convertInginiousLanguageToCodemirror(inginiousLanguage) {
    var languages = {
        "java7": "java",
        "java8": "java",
        "js": "javascript",
        "cpp": "cpp",
        "cpp11": "cpp",
        "c": "c",
        "c11": "c",
        "python2": "python",
        "python3": "python",
        "ruby": "ruby"
    };

    return languages[inginiousLanguage];
}

function studio_init_template_code_multiple_languages(well, pid, problem)
{
    if("type" in problem)
        $('#type-' + pid, well).val(problem["type"]);
    if("optional" in problem && problem["optional"])
        $('#optional-' + pid, well).attr('checked', true);

    if ("languages" in problem) {
        jQuery.each(problem["languages"], function(language, allowed) {
            if (allowed)
                $("#" + language + "-" + pid, well).attr("checked", true);
        });
    }
}

function toggleElement (id) {
    var element = document.getElementById(id);
    if (element.style.display === 'none') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}