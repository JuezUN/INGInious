function load_input_code_multiple_languages(submissionid, key, input) {
    load_input_code(submissionid, key, input);
    setDropDownWithTheRightLanguage(key, input[key + "/language"]);
    changeSubmissionLanguage(key);
}


function setDropDownWithTheRightLanguage(key, language) {
    const dropDown = document.getElementById(key + '/language');
    dropDown.value = language;
}

function changeSubmissionLanguage(key, problem_type) {
    if (problem_type === 'code_file_multiple_languages') return;

    const language = getLanguageForProblemId(key);
    const mode = CodeMirror.findModeByName(language);
    const editor = codeEditors[key];
    const lintingOptions = {
        async: true
    };

    //This should be first because setOption("mode", ...) triggers callbacks that call the linter
    editor.setOption("inginiousLanguage", getInginiousLanguageForProblemId(key));

    editor.setOption("mode", mode.mime);
    editor.setOption("gutters", ["CodeMirror-linenumbers", "CodeMirror-foldgutter", "CodeMirror-lint-markers"]);
    editor.setOption("lint", lintingOptions);
    CodeMirror.autoLoadMode(editor, mode["mode"]);
}

function getLanguageForProblemId(key) {
    return convertInginiousLanguageToCodemirror(getInginiousLanguageForProblemId(key));
}

function getInginiousLanguageForProblemId(key) {
    const dropDown = document.getElementById(key + '/language');
    if (dropDown == null)
        return "plain";

    const inginiousLanguage = dropDown.options[dropDown.selectedIndex].value;
    return inginiousLanguage;
}

function convertInginiousLanguageToCodemirror(inginiousLanguage) {
    const languages = {
        "java7": "java",
        "java8": "java",
        "cpp": "cpp",
        "cpp11": "cpp",
        "c": "c",
        "c11": "c",
        "python3": "python",
        "vhdl": "vhdl",
        "verilog": "verilog"
    };

    return languages[inginiousLanguage];
}

function studio_init_template_code_multiple_languages(well, pid, problem) {
    if ("type" in problem)
        $('#type-' + pid, well).val(problem["type"]);
    if ("optional" in problem && problem["optional"])
        $('#optional-' + pid, well).attr('checked', true);

    if ("languages" in problem) {
        jQuery.each(problem["languages"], function (language, allowed) {
            if (allowed)
                $("#" + language + "-" + pid, well).attr("checked", true);
        });
    }
}

function studio_init_template_notebook_file(well, pid, problem) {
    if ("type" in problem)
        $('#type-' + pid, well).val(problem["type"]);
}

function load_input_notebook_file(submissionid, key, input) {
    load_input_file(submissionid, key, input);
    const url = $('form#task').attr("action") + "?submissionid=" + submissionid + "&questionid=" + key;
    $.ajax({
        url: url,
        method: "GET",
        dataType: 'json',
        success: function (data) {
            render_notebook(data)
        }
    });
    highlight_code();
}

function studio_init_template_code_file_multiple_languages(well, pid, problem) {
    if ("max_size" in problem)
        $('#maxsize-' + pid, well).val(problem["max_size"]);
    if ("allowed_exts" in problem)
        $('#extensions-' + pid, well).val(problem["allowed_exts"].join());

    if ("languages" in problem) {
        jQuery.each(problem["languages"], function (language, allowed) {
            if (allowed)
                $("#" + language + "-" + pid, well).attr("checked", true);
        });
    }
}

function load_input_code_file_multiple_languages(submissionid, key, input) {
    load_input_file(submissionid, key, input);
    setDropDownWithTheRightLanguage(key, input[key + "/language"]);
}

let selected_all_languages = false;

function toggle_languages_checkboxes() {
    const environmentSelectElement = $("#environment");
    const problemId = getProblemId();

    selected_all_languages = !selected_all_languages;
    $(".checkbox_language").prop("checked", selected_all_languages);
    let text_button = "Select all";
    if (selected_all_languages) text_button = "Unselect All";
    $("#toggle_select_languages_button").text(text_button);

    if (!environmentSelectElement.length) return;

    if (environmentSelectElement.val() === "HDL") {
        $(".checkbox_language").prop("checked", false);
        $(`#vhdl-${problemId}`).prop('checked', selected_all_languages);
        $(`#verilog-${problemId}`).prop('checked', selected_all_languages);
    } else {
        $(`#vhdl-${problemId}`).prop('checked', false);
        $(`#verilog-${problemId}`).prop('checked', false);
    }
}

/**
 * Monkey patch `studio_subproblem_delete` to detect when a subproblem is deleted, that way
 * the options to create a new subproblem are displayed.
 */
const original_studio_subproblem_delete = this.studio_subproblem_delete;
this.studio_subproblem_delete = (pid) => {
    original_studio_subproblem_delete(pid);
    toggle_display_new_subproblem_option();
    showCorrectLanguagesEnvironment();
};

/**
 * Monkey patch `studio_create_new_subproblem` to detect when a subproblem is created, that way
 * the options to create a new subproblem are hidden.
 */
const original_studio_create_new_subproblem = this.studio_create_new_subproblem;
this.studio_create_new_subproblem = () => {
    original_studio_create_new_subproblem();
    toggle_display_new_subproblem_option();
};

function toggle_display_new_subproblem_option() {
    const container = $("#accordion");
    const new_subproblem_element = $("#new_subproblem");
    if (container.children().length) new_subproblem_element.hide();
    else new_subproblem_element.show();
}

const render_notebook = function (ipynb) {
    const notebook_holder = $("#notebook-holder")[0];
    $("#notebook-holder").hide();
    const notebook = this.notebook = nb.parse(ipynb);
    while (notebook_holder.hasChildNodes()) {
        notebook_holder.removeChild(notebook_holder.lastChild);
    }
    notebook_holder.appendChild(notebook.render());
    highlight_code();
    $("#notebook-holder").show();
};

function notebook_start_renderer() {
    const notebook_holder_html = '<div class="DivToScroll DivWithScroll" id="notebook-holder" hidden></div>'
    let taskAlert = $("#task_alert");
    taskAlert.after(notebook_holder_html);
    const load_file = function (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const parsed = JSON.parse(this.result);
            render_notebook(parsed);
        };
        reader.readAsText(file);
    };

    try {
        // Handle exception when getProblemId does not exists
        const file_input = $("input[name=" + getProblemId() + "]")[0];
        file_input.onchange = function (e) {
            const file = this.files[0];
            if (file === undefined || file.name.split('.')[1] !== 'ipynb') {
                $("#notebook-holder").html("");
                $("#notebook-holder").hide();
                return;
            }
            load_file(file);
        };
        file_input.onclick = function () {
            this.value = null;
            $("#notebook-holder").html("");
            $("#notebook-holder").hide();
        };
    } catch (e) {
    }
}

function sendSubmissionAnalytics() {
    $('#task-submit').on('click', function () {
        if (loadingSomething)
            return;

        if (!taskFormValid())
            return;

        const environments = new Set(['multiple_languages', 'Data Science', 'Notebook', 'HDL']);
        if (!environments.has(getTaskEnvironment()))
            return;

        const services = {
            'Notebook_notebook_file': [`${getTaskEnvironment()}_submission`, `${getTaskEnvironment()} submission`],
            'multiple_languages_code_multiple_languages': [`multiple_languages_code_multiple_languages`, `Multiple languages - Code submission`],
            'multiple_languages_code_file_multiple_languages': [`multiple_languages_code_file_multiple_languages`, `Multiple languages - File submission`],
            'Data Science_code_multiple_languages': [`data_science_code_multiple_languages`, `Data Science - Code submission`],
            'Data Science_code_file_multiple_languages': [`data_science_code_file_multiple_languages`, `Data Science - File submission`],
            'HDL_code_multiple_languages': [`HDL_code_multiple_languages`, `HDL - Code submission`],
            'HDL_code_file_multiple_languages': [`HDL_code_file_multiple_languages`, `HDL - File submission`],
        };

        $.post('/api/analytics/', {
            service: {
                key: services[`${getTaskEnvironment()}_${getProblemType()}`][0],
                name: services[`${getTaskEnvironment()}_${getProblemType()}`][1]
            }, course_id: getCourseId(),
        });
    });
}


function highlight_code() {
    Prism.highlightAll();
}

// These functions are intended to show the correct languages for multilang when the environment is HDL
// or multilang.
function getProblemId() {
    const problemId = $("#problem_id")[0];
    if (!problemId) return;
    return problemId.value;
}

function hideLanguages() {
    let problemId = getProblemId();
    $(`.checkbox_language_${problemId}`).prop("hidden", true);
}

function showLanguages() {
    const problemId = getProblemId();
    $(`.checkbox_language_${problemId}`).prop("hidden", false);
}

function showCorrectLanguagesEnvironment() {
    const problemId = getProblemId();

    const environmentSelectElement = $("#environment");
    if (!environmentSelectElement.length) return;

    if (environmentSelectElement.val() === "HDL") {
        hideLanguages();
        $(`.checkbox_${problemId}_vhdl`).prop('hidden', false);
        $(`.checkbox_${problemId}_verilog`).prop('hidden', false);
    } else {
        showLanguages();
        $(`.checkbox_${problemId}_vhdl`).prop('hidden', true);
        $(`.checkbox_${problemId}_verilog`).prop('hidden', true);
    }
}

jQuery(document).ready(function () {
    const environmentSelectElement = $("#environment");
    if (environmentSelectElement.length) {
        environmentSelectElement.on('change', showCorrectLanguagesEnvironment);
    }
    showCorrectLanguagesEnvironment();
    toggle_display_new_subproblem_option();
    notebook_start_renderer();
    sendSubmissionAnalytics();
});
