function updateCodePreviewFiles() {
    $.get("/api/grader_generator/test_file_api", {
        course_id: getCourseId(),
        task_id: getTaskId(),
    }, function (files) {
        let previewFileSelect = $("#code_preview_files");

        previewFileSelect.empty();

        $.each(files, function (index, file) {
            const fileIsTestCase = file.complete_name.includes(".in") || file.complete_name.includes(".out");
            if (file.is_directory || fileIsTestCase || file.complete_name === "run") {
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
    const codePreviewLanguagesElem = $("#code_preview_languages");
    $(".code_preview_language").remove();
    codePreviewLanguagesElem.append(`<option class="code_preview_language" value="-1">${getSelectOneMessage()}</option>`);
    for (let i = 0; i < languages.length; i++) {
        if (languages[i].checked) {
            codePreviewLanguagesElem.append(
                `<option class="code_preview_language"  
                         value="${languages[i].value}">${getLanguageName(languages[i].value)}</option>`);
        }
    }
}

/**
 * Function that calls an API to get the code template for the given course, task and language.
 * In case a template file is associated to the language, it sets the code to Codemirror.
 */
function loadCodePreviewToCodemirror() {
    $.get("/api/code_preview/", {
        task_id: getTaskId(),
        course_id: getCourseId(),
        language: getInginiousLanguageForProblemId(getProblemId())
    }).done(function write(result) {
        const keysCodeEditors = Object.keys(codeEditors);
        keysCodeEditors.forEach((element) => {
            codeEditors[element].setValue(result);
        });
    });
}

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

jQuery(document).ready(function () {
    if (typeof getTaskEnvironment !== "undefined"
        && ["multiple_languages", "HDL", "Data Science"].includes(getTaskEnvironment())
        && !location.href.includes("submission")) {
        monkeyPatchChangeSubmissionLanguage();
        loadCodePreviewToCodemirror();
    }
});