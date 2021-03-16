const multiLangTestCaseParameters = ["input_file", "output_file", "weight", "custom_feedback", "diff_shown"];
const multiLangButtons = [new Button("delete_btn", "studio_remove_test_case")];

let grader_test_cases_count = 0;
let test_cases_input = [];

function studio_add_test_case_from_form() {
    studio_add_test_case({
        "input_file": $("#grader_test_case_in").val(),
        "output_file": $("#grader_test_case_out").val()
    });
    updateMainShowDiffsCheckbox();
}

function studio_add_test_case(test_case) {
    test_case = $.extend({
        "input_file": null,
        "output_file": null,
        "weight": 1.0,
        "custom_feedback": "",
        "diff_shown": false
    }, test_case);

    const test_id = grader_test_cases_count;

    const inputFile = test_case["input_file"];
    const outputFile = test_case["output_file"];

    if (!inputFile || !outputFile) {
        return;
    }

    const template = $("#test_case_template").html().replace(/TID/g, test_id);

    const templateElement = $(template);

    insertDataContent(templateElement, test_case);

    grader_test_cases_count++;
    test_cases_input.push(inputFile);

    hideOrShowHeader();

    $('#grader_test_cases_container').append(templateElement);
}

function insertDataContent(templateElement, test_data) {
    const baseId = templateElement.attr("id");
    const subArrayParameters = multiLangTestCaseParameters.slice(0, -1);

    $.each(subArrayParameters, (_, parameterId) => {
            templateElement.find(`#${baseId}_${parameterId}`).val(test_data[parameterId]);
        }
    );

    templateElement.find(`#${baseId}_diff_shown`).prop('checked', test_data["diff_shown"]);
}


function getIdNum(id) {
    const baseIdPrefixLen = "grader_test_cases_".length;
    return id.substr(baseIdPrefixLen);
}

function multiLangLoadAllTests(testCases) {
    $.each(testCases, function (_, testCase) {
        studio_add_test_case(testCase);
    });
}

function studio_remove_test_case(id) {
    const baseId = `grader_test_cases_${id}`;
    const inputFileName = $(`#${baseId}_input_file`).val();
    const indexToDelete = test_cases_input.indexOf(inputFileName);

    $(`#${baseId}`).remove();
    correctIds(id);
    grader_test_cases_count--;

    hideOrShowHeader();
    test_cases_input.splice(indexToDelete, 1);
}

function hideOrShowHeader() {
    if (grader_test_cases_count === 0) {
        $('#grader_test_cases_header').hide();
    } else {
        $('#grader_test_cases_header').show();
    }
}

function correctIds(idDeleted) {
    for (let i = idDeleted + 1; i < grader_test_cases_count; i++) {
        updateTestInternalIds(i, i - 1);
    }
}

function studio_update_grader_problems() {
    let container = $("#accordion");

    let problems = [];
    $.each(container.children(), function (index, value) {
        let id = value.id;
        let prefix = "subproblem_well_";
        if (!id.startsWith(prefix)) {
            throw new Error("Unable to process problem well: " + id);
        }

        let problemId = id.substring(prefix.length);
        let type = $(value).find("[name='problem[" + problemId + "][type]']").val();

        problems.push({
            "id": problemId,
            "type": type
        });
    });

    const graderSelect = $("#grader_problem_id");
    let currentlySelectedItem = graderSelect.val();

    graderSelect.empty();
    const accepted_problems = ["code_multiple_languages", "code_file_multiple_languages", "notebook_file"];
    $.each(problems, function (index, problem) {
        if (accepted_problems.indexOf(problem.type) !== -1) {
            graderSelect.append($("<option>", {
                "value": problem.id,
                "text": problem.id
            }));
            currentlySelectedItem = problem.id;
        }
    });

    graderSelect.val(currentlySelectedItem);
}

function studio_set_initial_problem(initialProblemId) {
    const graderSelect = $("#grader_problem_id");
    const generateGraderIsChecked = $("#generate_grader").is(':checked');
    let selectedItem = initialProblemId;
    if (generateGraderIsChecked && initialProblemId) {
        selectedItem = initialProblemId;
        graderSelect.append($("<option>", {
            "value": initialProblemId,
            "text": initialProblemId
        }));
    }
    graderSelect.val(selectedItem);
}

function studio_update_grader_files() {
    const container_name = $("#environment").val();
    if (container_name === "Notebook") return;

    $.get('/api/grader_generator/test_file_api', {
        course_id: courseId,
        task_id: taskId
    }, function (files) {
        const inputFileSelect = $("#grader_test_case_in");
        const outputFileSelect = $("#grader_test_case_out");
        const testbechFileSelect = $("#testbench_file_name");
        const hdlOutputFileSelect = $("#hdl_expected_output");

        inputFileSelect.empty();
        outputFileSelect.empty();
        testbechFileSelect.empty();
        hdlOutputFileSelect.empty();

        $.each(files, function (index, file) {
            if (file.is_directory) {
                return;
            }

            // Do not set run file as an option.
            if (file.complete_name === 'run') {
                return;
            }

            let entry = $("<option>", {
                "value": file.complete_name,
                "text": file.complete_name
            });

            inputFileSelect.append(entry);
            outputFileSelect.append(entry.clone());
            testbechFileSelect.append(entry.clone());
            hdlOutputFileSelect.append(entry.clone());
        });
    }, "json");

}

function studio_update_container_name() {
    // This function hides the forms which container is not been used
    // Check container (environment) name, and hide all test containers
    const container_name = $("#environment").val();
    const test_containers = $(".grader_form");
    const tab_grader_element = $("#tab_grader");
    tab_grader_element.find("div.form-group")[2].style.display = "block";
    tab_grader_element.find("div.form-group")[3].style.display = "block";
    for (let cont = 0; cont < test_containers.length; cont++) {
        test_containers[cont].style.display = "none";
    }

    try {
        switch (container_name) {
            case "Notebook":
                $("#notebook_grader_form")[0].style.display = "block";
                // Do not show diff related inputs
                tab_grader_element.find("div.form-group")[2].style.display = "none";
                tab_grader_element.find("div.form-group")[3].style.display = "none";
                break;
            case "HDL":
                $("#hdl_grader_form")[0].style.display = "block";
                break;
            case "multiple_languages":
            case "Data Science":
                $("#multilang_grader_form")[0].style.display = "block";
        }
    } catch {
    }
}

// Match test cases
function read_files_and_match() {
    const container_name = $("#environment").val();
    if (container_name === "Notebook" || container_name === "HDL") return;

    // This function reads all the files on the tab "Task files" and
    // matches to test cases
    $.get('/api/grader_generator/test_file_api', {
        course_id: courseId,
        task_id: taskId
    }, function (files) {
        // Pass the file info to JSON for comparison

        $.each(files, function (index, file) {
            if (file.is_directory) {
                return;
            }

            let entry = {};
            const parts = file.name.split('.');
            const complete_parts = file.complete_name.split('.');
            const name_without_extension = parts.splice(0, parts.length - 1).join(".");
            const complete_name_output = complete_parts.splice(0, complete_parts.length - 1).join(".") + '.out';


            if (test_cases_input.includes(file.name)) {
                return;
            }

            if (parts[parts.length - 1] === 'in') {
                const file_obj = {
                    "level": file.level,
                    "complete_name": complete_name_output,
                    "name": name_without_extension + '.out',
                    "is_directory": false
                };
                for (let ind = 0; ind < files.length; ind++) {
                    const el = files[ind];
                    if (el.complete_name === file_obj.complete_name && el.is_directory === file_obj.is_directory) {
                        entry = {
                            'input_file': file.complete_name,
                            'output_file': file_obj.complete_name
                        };
                        studio_add_test_case(entry);
                    }
                }
            }
        });
    }, "json");
}

/** Utilities
 * Toggle selection: selects all in case that some or none test cases are selected
 * and unselects all in case that all test cases are selected
 *
 * Remove all: Removes all the test cases
 */


function remove_all_test_cases() {
    for (let i = 0; i < grader_test_cases_count; i++) {
        studio_remove_test_case(i);
    }
    grader_test_cases_count = 0;

}

function expand_text_area(elem, rows = 6) {
    elem.rows = rows;
}

function compress_text_area(elem, rows = 2) {
    elem.rows = rows;
}
