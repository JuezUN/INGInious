function loadCodePreviewToCodemirror() {
    // TODO: Change the way this is checked as LTI does not work with this.
    if (location.href.indexOf("/course") > -1 && location.href.split('/').length === 6) {
        $.get("/api/code_preview/", {
            task_id: getTaskId(),
            course_id: getCourseId(),
            language: getInginiousLanguageForProblemId(getProblemId())
        }, function write(result) {
            const ks = Object.keys(codeEditors);
            ks.forEach(element => {
                codeEditors[element].setValue(result);
            });
        });
    }
}

function updateCodePreviewFiles() {
    $.get("/api/grader_generator/test_file_api", {
        course_id: getCourseId(),
        task_id: getTaskId(),
    }, function (files) {
        let previewFileSelect = $("#code_preview_files");

        previewFileSelect.empty();

        $.each(files, function (index, file) {
            const file_is_test_case = file.complete_name.includes(".in") || file.complete_name.includes(".out");
            if (file.is_directory || file_is_test_case || file.complete_name === "run") {
                return;
            }

            const entry = $("<option>", {
                "value": file.complete_name,
                "text": file.complete_name
            });

            previewFileSelect.append(entry);

        });
    }, "json");
}

function addCodePreviewPair() {
    const language = $("#code_preview_languages > option:selected")[0].value;
    const file = $("#code_preview_files > option:selected")[0].value;

    if (language === "-1") {
        return;
    }
    if (language in currentCodePreviewPairs) {
        currentCodePreviewPairs[language] = file;
        $(`#code_preview_pairs_${language}`).val(file);
        return;
    }

    const template = `
    <div class="row" id="code-preview-${language}-row">
        <div class="form-group col-xs-12">
            <div class="col-xs-4">
                <select class="form-control" readonly>
                    <option selected>${getLanguageName(language)}</option>
                </select>
            </div>
            <div class="col-xs-4">
                <input type=text class="form-control" id="code_preview_pairs_${language}" name="code_preview_pairs[${language}]" value="${file}" readonly />
            </div>
            <div class="col-xs-4" style="display: flex; height: 100%">
                <button type="button" class="btn btn-danger btn-block" style="align-self: flex-end;"
                onclick="removeCodePreviewPair('${language}');">${getRemoveMessage()}</button>
        </div>
    </div>
    `;

    currentCodePreviewPairs[language] = file;
    $("#code_preview_files_pairs").append(template);
}

function removeCodePreviewPair(key) {
    delete currentCodePreviewPairs[key];
    $(`#code-preview-${key}-row`).remove();
}

function updateCodePreviewLanguages() {
    // Get the selected languages in subproblems tab.
    const languages = $(".checkbox_language");
    $(".code_preview_language").remove();
    $("#code_preview_languages").append(`<option class="code_preview_language" value="-1">${getSelectOneMessage()}</option>`);
    for (let i = 0; i < languages.length; i++) {
        if (languages[i].checked)
            $("#code_preview_languages").append(
                `<option class="code_preview_language"  
                         value="${languages[i].value}">${getLanguageName(languages[i].value)}</option>`);
    }
}

$("a[data-toggle='tab'][href='#tab_code_preview']").on("show.bs.tab", function (e) {
    updateCodePreviewLanguages();
    updateCodePreviewFiles();
    const environment = $("#environment").val();
    if (["HDL", "multiple_languages"].includes(environment)) {
        $("#code_preview button").prop("disabled", false);
        $("#code_preview select").prop("disabled", false);
    } else {
        $("#code_preview button").prop("disabled", true);
        $("#code_preview select").prop("disabled", true);
    }
});

/**
 * Monkey-patch the function `changeSubmissionLanguage` from multilang plugin to run the function
 * `loadCodePreviewToCodemirror`, which loads the code preview to Codemirror when the submission language is changed.
 */
function monkeyPatchChangeSubmissionLanguage() {
    const changeSubmissionLanguageOriginal = changeSubmissionLanguage;
    changeSubmissionLanguage = (key, problem_type) => {
        changeSubmissionLanguageOriginal(key, problem_type);
        loadCodePreviewToCodemirror();
    };
}

jQuery(document).ready(function () {
    if (typeof getProblemId !== "undefined") {
        monkeyPatchChangeSubmissionLanguage();
        loadCodePreviewToCodemirror();
    }
});