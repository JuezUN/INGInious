let studio_grader_test_case_sequence = 0;
let grader_test_cases_count = 0;
let test_cases_input = [];
let ids_test_cases_input = [];

function studio_add_test_case_from_form() {
    studio_add_test_case({
        "input_file": $("#grader_test_case_in").val(),
        "output_file": $("#grader_test_case_out").val()
    });
}

function studio_add_test_case(test_case) {
    test_case = $.extend({
        "input_file": null,
        "output_file": null,
        "weight": 1.0,
        "diff_shown": false
    }, test_case);

    let test_id = studio_grader_test_case_sequence;

    let inputFile = test_case["input_file"];
    let outputFile = test_case["output_file"];

    if (!inputFile || !outputFile) {
        return;
    }

    let template = $("#test_case_template").html().replace(/TID/g, test_id);

    let templateElement = $(template);
    templateElement.find("#grader_test_cases_" + test_id + "_input_file").val(inputFile);
    templateElement.find("#grader_test_cases_" + test_id + "_output_file").val(outputFile);
    templateElement.find("#grader_test_cases_" + test_id + "_weight").val(
        test_case["weight"]);
    templateElement.find("#grader_test_cases_" + test_id + "_diff_shown").prop('checked',
        test_case["diff_shown"]);

    studio_grader_test_case_sequence++;
    grader_test_cases_count++;
    test_cases_input.push(inputFile);
    ids_test_cases_input.push(test_id)

    let first_row = (grader_test_cases_count == 1);

    if (first_row) {
        $('#grader_test_cases_header').show();
    }

    $('#grader_test_cases_container').append(templateElement);
}

function studio_load_grader_test_cases(test_cases) {
    if ($("#environment").val() === "Notebook") {
        notebook_grader_load_all_tests(test_cases)
    } else {
        $.each(test_cases, function (_, test_case) {
            studio_add_test_case(test_case);
        });
    }
}

function studio_remove_test_case(id) {
    $("#grader_test_cases_" + id).remove();
    grader_test_cases_count--;
    if (grader_test_cases_count == 0) {
        $('#grader_test_cases_header').hide();
    }
    let ind_of_test_case = ids_test_cases_input.findIndex(el => el === id);
    test_cases_input.splice(ind_of_test_case, 1);
    ids_test_cases_input.splice(ind_of_test_case, 1);
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

    let graderSelect = $("#grader_problem_id");
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
    let graderSelect = $("#grader_problem_id");
    let generateGraderIsChecked = $("#generate_grader").is(':checked');
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
        let inputFileSelect = $("#grader_test_case_in");
        let outputFileSelect = $("#grader_test_case_out");
        let testbechFileSelect = $("#testbench_file_name");
        let hdlOutputFileSelect = $("#hdl_expected_output");

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
    $("#tab_grader").find("div.form-group")[2].style.display = "block";
    $("#tab_grader").find("div.form-group")[3].style.display = "block";
    for (let cont = 0; cont < test_containers.length; cont++) {
        test_containers[cont].style.display = "none";
    }

    try {
        switch (container_name) {
            case "Notebook":
                $("#notebook_grader_form")[0].style.display = "block";
                // Do not show diff related inputs
                $("#tab_grader").find("div.form-group")[2].style.display = "none";
                $("#tab_grader").find("div.form-group")[3].style.display = "none";
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
            let parts = file.name.split('.');
            let complete_parts = file.complete_name.split('.')
            let name_without_extension = parts.splice(0, parts.length - 1).join(".");
            let complete_name_output = complete_parts.splice(0, complete_parts.length - 1).join(".") + '.out';


            if (test_cases_input.includes(file.name)) {
                return;
            }

            if (parts[parts.length - 1] === 'in') {
                let file_obj = {
                    "level": file.level,
                    "complete_name": complete_name_output,
                    "name": name_without_extension + '.out',
                    "is_directory": false
                };
                for (ind = 0; ind < files.length; ind++) {
                    var el = files[ind];
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

function toggle_selection_tests_cases() {
    var option = $("#toggle_select_test_cases")[0].checked;
    // Activate in case of button press and not checkbox
    option = !option;
    $("#toggle_select_test_cases").prop("checked", option);

    ids_test_cases_input.forEach((item, _) => {
        $("#grader_test_cases_" + item + "_diff_shown").prop("checked", option);
    })

}

function remove_all_test_cases() {
    var to_delete = ids_test_cases_input.slice();
    to_delete.forEach((item, _) => {
        studio_remove_test_case(item);
    });
}
