let grader_test_cases_count = 0;
let test_cases_input = [];

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

    templateElement.find(`#${baseId}_input_file`).val(test_data["input_file"]);
    templateElement.find(`#${baseId}_output_file`).val(test_data["output_file"]);
    templateElement.find(`#${baseId}_weight`).val(test_data["weight"]);
    templateElement.find(`#${baseId}_custom_feedback`).val(test_data["custom_feedback"]);
    templateElement.find(`#${baseId}_diff_shown`).prop('checked', test_data["diff_shown"]);
}


function getIdNum(id) {
    const baseIdPrefixLen = "grader_test_cases_".length;
    return id.substr(baseIdPrefixLen);
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
        updateItemIds(i, i - 1);
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

function toggle_selection_tests_cases() {
    const option = !($("#toggle_select_test_cases")[0].checked);
    // Activate in case of button press and not checkbox
    $("#toggle_select_test_cases").prop("checked", option);

    for (let i = 0; i < grader_test_cases_count; i++) {
        $(`#grader_test_cases_${i}_diff_shown`).prop("checked", option);
    }

}

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

function addSwitchBehavior() {
    function shiftClasses(object) {
        object.find('.btn').toggleClass('active');
        object.find('.btn').toggleClass('btn-primary');
        object.find('.btn').toggleClass('btn-default');
    }

    $('.btn-toggle').click(function () {
        shiftClasses($(this));
    });

}


function activeSortableMode() {
    const testCases = $("#grader_test_cases_container")[0];
    //TODO: add comments
    Sortable.create(testCases, {
        group: "test-cases",
        animation: 150,
        easing: "cubic-bezier(0.895, 0.03, 0.685, 0.22)",
        handle: ".item-cursor-move",
        chosenClass: "active",
        onEnd: (moveEvent) => {
            const oldPos = moveEvent["oldIndex"];
            const newPos = moveEvent["newIndex"];
            updateAllIds(oldPos, newPos);
        }
    });
}

function updateAllIds(oldPos, newPos) {
    const itemPosIncreased = (oldPos - newPos) < 0;
    if (itemPosIncreased) {
        updateIdsLowestToHighest(oldPos, newPos);
    } else {
        updateIdsHighestToLowest(oldPos, newPos);
    }

}

function updateIdsHighestToLowest(oldPos, newPos) {
    const auxName = "AUX"
    updateItemIds(oldPos, auxName);
    for (let i = oldPos - 1; i >= newPos; i--) {
        updateItemIds(i, i + 1);
    }
    updateItemIds(auxName, newPos)

}

function updateIdsLowestToHighest(oldPos, newPos) {
    const auxName = "AUX"
    updateItemIds(oldPos, auxName);
    for (let i = oldPos + 1; i <= newPos; i++) {
        updateItemIds(i, i - 1);
    }
    updateItemIds(auxName, newPos)

}

function updateItemIds(itemId, newPos) {
    const oldId = `grader_test_cases_${itemId}`
    const newId = `grader_test_cases_${newPos}`;
    const newName = `grader_test_cases[${newPos}]`;

    const template = $(`#${oldId}`);
    const input = $(`#${oldId}_input_file`);
    const output = $(`#${oldId}_output_file`);
    const weight = $(`#${oldId}_weight`);
    const diff = $(`#${oldId}_diff_shown`);
    const feedback = $(`#${oldId}_custom_feedback`);
    const btn = $(`#${oldId}_delete_btn`);

    input.attr("id", `${newId}_input_file`);
    input.attr("name", `${newName}[input_file]`);
    output.attr("id", `${newId}_output_file`);
    output.attr("name", `${newName}[output_file]`);
    weight.attr("id", `${newId}_weight`);
    weight.attr("name", `${newName}[weight]`);
    diff.attr("id", `${newId}_diff_shown`);
    diff.attr("name", `${newName}[diff_shown]`)
    feedback.attr("id", `${newId}_custom_feedback`);
    feedback.attr("name", `${newName}[custom_feedback]`);
    btn.attr("id", `${newId}_delete_btn`);
    btn.attr("onclick", `studio_remove_test_case(${newPos})`);
    template.attr("id", newId);

}
