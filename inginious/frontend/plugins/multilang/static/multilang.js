function load_input_code_multiple_languages(submissionid, key, input) {
    load_input_code(submissionid, key, input);
    setDropDownWithTheRightLanguage(key, input[key + "/language"]);
    changeSubmissionLanguage(key);
}

function onChangeLanguageDropdown(key, problem) {
    changeSubmissionLanguage(key, problem);
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
        async: true,
        lintOnChange: false
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

    return dropDown.options[dropDown.selectedIndex].value;
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
            render_notebook(data, $("#notebook-holder"))
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
    const problemId = getProblemIdEdit();

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
    } else if (environmentSelectElement.val() === "Data Science") {
        $(".checkbox_language").prop("checked", false);
        $(`#python3-${problemId}`).prop('checked', selected_all_languages);
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

const render_notebook = function (ipynb, notebook_holder_element) {
    const notebook_holder = notebook_holder_element[0];
    notebook_holder_element.hide();
    const notebook = this.notebook = nb.parse(ipynb);
    while (notebook_holder.hasChildNodes()) {
        notebook_holder.removeChild(notebook_holder.lastChild);
    }
    notebook_holder.appendChild(notebook.render());
    highlight_code();
    notebook_holder_element.show();
};

function notebook_start_renderer() {
    const notebook_holder_html = '<div class="DivToScroll DivWithScroll" id="notebook-holder" hidden></div>'
    let taskAlert = $("#task_alert");
    taskAlert.after(notebook_holder_html);
    const load_file = function (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const parsed = JSON.parse(this.result);
            render_notebook(parsed, $("#notebook-holder"));
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

        // The button related to late submissions has the attribute `late-submission`. In case it is a late
        // submission, modify the key and name for the service adding at the end `late`.
        const lateSubmission = $(this).attr("late-submission");
        let lateSubmissionData = {key: "", name: ""};
        if (typeof lateSubmission !== "undefined" && lateSubmission !== false) {
            lateSubmissionData["key"] = "_late";
            lateSubmissionData["name"] = " - Late";
        }

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
                key: services[`${getTaskEnvironment()}_${getProblemType()}`][0] + lateSubmissionData["key"],
                name: services[`${getTaskEnvironment()}_${getProblemType()}`][1] + lateSubmissionData["name"]
            }, course_id: getCourseId(),
        });
    });
}


function highlight_code() {
    Prism.highlightAll();
}

// These functions are intended to show the correct languages for multilang when the environment is HDL
// or multilang.
function getProblemIdEdit() {
    const problemId = $("#problem_id")[0];
    if (!problemId) return;
    return problemId.value;
}

function hideLanguages() {
    const problemId = getProblemIdEdit();
    $(`.checkbox_language_${problemId}`).prop("hidden", true);
}

function showLanguages() {
    const problemId = getProblemIdEdit();
    $(`.checkbox_language_${problemId}`).prop("hidden", false);
}

function showCorrectLanguagesEnvironment(uncheckBoxes = true) {
    const problemId = getProblemIdEdit();

    const environmentSelectElement = $("#environment");
    if (!environmentSelectElement.length) return;

    if (uncheckBoxes) $(".checkbox_language").prop("checked", false);
    if (environmentSelectElement.val() === "HDL") {
        hideLanguages();
        $(`.checkbox_${problemId}_vhdl`).prop('hidden', false);
        $(`.checkbox_${problemId}_verilog`).prop('hidden', false);
    } else if (environmentSelectElement.val() === "Data Science") {
        hideLanguages();
        $(`.checkbox_${problemId}_python3`).prop('hidden', false);
    } else {
        showLanguages();
        $(`.checkbox_${problemId}_vhdl`).prop('hidden', true);
        $(`.checkbox_${problemId}_verilog`).prop('hidden', true);
    }
}

function setupGradingEnvironmentView() {
    const environmentSelectElement = $("#environment");
    if (environmentSelectElement.length) {
        environmentSelectElement.on('change', function () {
            configEnvironmentView()
        });
    }
    configEnvironmentView(false);
}

function configEnvironmentView(uncheckBoxes = true) {
    showCorrectLanguagesEnvironment(uncheckBoxes);
    blockUnusedLimitInputs();
    showCorrectSubProblemsTypes();
}

function blockUnusedLimitInputs() {
    const selectedEnvironmentVal = $("#environment").val();
    const limitsToBlockIds = ["limit-time", "limit-hard-time", "limit-memory", "limit-output"];
    const environmentWhichUsesLimits = "HDL";
    const isUsingLimits = selectedEnvironmentVal === environmentWhichUsesLimits;
    $.each(limitsToBlockIds, (_, id) => {
        $(`#${id}`).prop('readonly', !isUsingLimits);
    });

}

function showCorrectSubProblemsTypes() {
    const selectedEnvironmentVal = $("#environment").val();
    const notebookTypeValue = ["subproblem_notebook_file"];
    const multipleLangTypeValue = ["subproblem_code_multiple_languages", "subproblem_code_file_multiple_languages"];

    function blockOrUnlockOptions(types, block = false) {
        $.each(types, (_, type) => {
            $(`#new_subproblem_type option[value=${type}]`).enable(block);
        });
    }

    function selectOption(selection) {
        $(`#new_subproblem_type option`).each(function (index, element) {
            element.selected = false;
        });
        $(`#new_subproblem_type option[value=${selection}]`).attr("selected", true);
    }

    if (selectedEnvironmentVal === "Notebook") {
        blockOrUnlockOptions(notebookTypeValue, true);
        blockOrUnlockOptions(multipleLangTypeValue);
        selectOption(notebookTypeValue[0]);
    } else {
        blockOrUnlockOptions(multipleLangTypeValue, true);
        blockOrUnlockOptions(notebookTypeValue);
        selectOption(multipleLangTypeValue[0]);
    }
}

function hideRandomInputForm() {
    $("#randomInputForm").hide();
    $("#accessibleDivForm").css({"padding-bottom": "1rem"});
}

jQuery(document).ready(function () {
    hideRandomInputForm();
    setupGradingEnvironmentView();
    toggle_display_new_subproblem_option();
    notebook_start_renderer();
    sendSubmissionAnalytics();
});
