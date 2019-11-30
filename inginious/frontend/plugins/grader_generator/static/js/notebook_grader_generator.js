let notebook_grader_tests_sequence = 0;
let notebook_grader_tests_cases_count = {};
let editing_test_id = null;

const modal_element = $("#notebook_grader_test_form_modal");

function notebook_grader_add_test_case_from_form() {
    const test_id = notebook_grader_tests_sequence;
    const new_test_case = notebook_grader_create_test_case({
        "input_code": $("#notebook_grader_test_case_input_code").val(),
        "output_code": $("#notebook_grader_test_case_output_code").val(),
    });
    if (!new_test_case) return;

    const first_row = (notebook_grader_tests_cases_count[test_id] === 1);
    if (first_row) {
        $('#notebook_grader_test_cases_header').show();
    }

    $("#notebook_grader_test_cases_container").append(new_test_case);
    codeEditors["notebook_grader_test_case_input_code"].getDoc().setValue("");
    codeEditors["notebook_grader_test_case_output_code"].getDoc().setValue("");
    $(`#${new_test_case.attr('id')} .form-control`).each(function (index, elem) {
        registerCodeEditor(elem, $(elem).attr('data-x-language'), $(elem).attr('data-x-lines'));
    });
}

function notebook_grader_create_test_case(test_case_data) {
    test_case_data = $.extend({
        "input_code": null,
        "output_code": null
    }, test_case_data);

    const test_id = editing_test_id !== null ? editing_test_id : notebook_grader_tests_sequence;

    if (!notebook_grader_tests_cases_count[test_id]) {
        notebook_grader_tests_cases_count[test_id] = 0;
    }

    const case_id = notebook_grader_tests_cases_count[test_id],
        inputCode = test_case_data["input_code"],
        outputCode = test_case_data["output_code"];

    if (!inputCode || !outputCode) return;
    notebook_grader_tests_cases_count[test_id]++;
    return _notebook_grader_get_test_case_element(test_id, case_id, inputCode, outputCode);
}

function notebook_grader_remove_test_case(test_id, case_id) {
    const new_test_cases = _notebook_grader_shift_test_cases(test_id, case_id, "notebook_grader_test_cases_container");
    const container_element = $("#notebook_grader_test_cases_container");
    container_element.html("");
    $.each(new_test_cases, (_, test_case) => {
        container_element.append(test_case);
        $(`#${test_case.attr('id')} .form-control`).each(function (index, elem) {
            registerCodeEditor(elem, $(elem).attr('data-x-language'), $(elem).attr('data-x-lines'));
        });
    });

    notebook_grader_tests_cases_count[test_id]--;
    if (notebook_grader_tests_cases_count[test_id] === 0) {
        $('#notebook_grader_test_cases_header').hide();
    }
}

/**
 * This function shifts to the left all test cases, avoiding the test case to delete.
 * This is to update the HTML ids and names to have a better counting.
 */
function _notebook_grader_shift_test_cases(test_id, case_id_to_remove) {
    const amount_cases = notebook_grader_tests_cases_count[test_id];
    const test_cases = [];
    let case_id = 0;
    for (let index = 0; index < amount_cases; index++) {
        if (index === case_id_to_remove) continue;
        const input_code = $(`#notebook_grader_test_${test_id}_cases_${index}_input_code`).val();
        const output_code = $(`#notebook_grader_test_${test_id}_cases_${index}_output_code`).val();
        const new_test_case = _notebook_grader_get_test_case_element(test_id, case_id, input_code, output_code);
        test_cases.push(new_test_case);
        case_id++;
    }
    return test_cases;
}

function _notebook_grader_get_test_case_element(test_id, case_id, input_code, output_code) {
    const template = $("#notebook_test_case_template").html().replace(/TID/g, test_id).replace(/CID/g, case_id);
    const template_element = $(template);

    template_element.find(`#notebook_grader_test_${test_id}_cases_${case_id}_input_code`).text(input_code);
    template_element.find(`#notebook_grader_test_${test_id}_cases_${case_id}_output_code`).text(output_code);
    return template_element;
}

function _notebook_grader_get_test_element(test_id, test_data, test_cases) {
    const template = $("#notebook_grader_test_template").html().replace(/TID/g, test_id);
    const test_name = test_data["name"], test_weight = test_data["weight"],
        setup_code = test_data["setup_code"];

    const template_element = $(template);
    template_element.find(`#notebook_grader_test_${test_id}_name`).val(test_name);
    template_element.find(`#notebook_grader_test_${test_id}_weight`).val(test_weight);
    template_element.find(`#notebook_grader_test_${test_id}_setup_code`).text(setup_code);

    $.each(test_cases, (_, test_case) => {
        template_element.find(`#notebook_grader_test_${test_id}_cases_container`).append(test_case);
    });
    return template_element;
}

function _notebook_grader_get_test_cases_from_container(test_id, container_id) {
    const amount_cases = notebook_grader_tests_cases_count[test_id];
    const test_cases_element = $(`#${container_id}`);
    const test_cases = [];
    for (let case_id = 0; case_id < amount_cases; case_id++) {
        const case_element = test_cases_element.find(`#notebook_grader_test_${test_id}_cases_${case_id}`);
        test_cases.push(case_element);
    }
    return test_cases;
}

function notebook_grader_add_test_from_form() {
    const test_id = notebook_grader_tests_sequence;
    const test_cases = _notebook_grader_get_test_cases_from_container(test_id, "notebook_grader_test_cases_container");
    const new_test = notebook_grader_create_test({
        "name": $("#notebook_grader_test_name").val(),
        "weight": $("#notebook_grader_test_weight").val(),
        "setup_code": $("#notebook_grader_test_setup_code").val()
    }, test_cases);

    if (!new_test) return;

    const first_row = (notebook_grader_tests_sequence === 1);
    if (first_row) {
        $('#notebook_grader_tests_header').show();
    }

    $('#notebook_grader_tests_container').append(new_test);
    modal_element.modal('hide');
}

function notebook_grader_create_test(test_data, test_cases) {
    test_data = $.extend({
        "name": "test",
        "weight": 1.0,
        "setup_code": "",
    }, test_data);

    const test_id = notebook_grader_tests_sequence, test_name = test_data["name"],
        test_weight = test_data["weight"];

    if (!notebook_grader_tests_cases_count[test_id]) {
        notebook_grader_tests_cases_count[test_id] = 0;
    }

    if (!test_name || !test_weight || !test_cases.length) return;
    notebook_grader_tests_sequence++;
    return _notebook_grader_get_test_element(test_id, test_data, test_cases);
}

function notebook_grader_load_all_tests(tests) {
    $.each(tests, function (test_id, test) {
        const test_cases = [];
        $.each(test["cases"], (case_id, test_case) => {
            const new_test_case = notebook_grader_create_test_case(test_case);
            test_cases.push(new_test_case);
        });
        const new_test = notebook_grader_create_test(test, test_cases);
        $(`#notebook_grader_tests_header`).show();
        $(`#notebook_grader_tests_container`).append(new_test);
    });
}

function notebook_grader_remove_test(test_id) {
    const new_tests = _notebook_grader_update_tests_ids(test_id);
    const container_element = $("#notebook_grader_tests_container");
    container_element.html("");
    $.each(new_tests, (_, test) => {
        container_element.append(test);
    });
    notebook_grader_tests_sequence--;
    if (notebook_grader_tests_sequence === 0) {
        $('#notebook_grader_tests_header').hide();
    }
}

/**
 * This function shifts to the left all test cases, avoiding the test case to delete.
 * This is to update the HTML ids and names to have a better counting.
 */
function _notebook_grader_update_tests_ids(test_id_to_remove) {
    const amount_tests = notebook_grader_tests_sequence;
    const tests = [];
    let new_test_id = 0, test_index = 0;
    for (; test_index < amount_tests; test_index++) {
        if (test_index === test_id_to_remove) continue;
        const test_cases = [];
        const test_cases_amount = notebook_grader_tests_cases_count[test_index];
        for (let case_index = 0; case_index < test_cases_amount; case_index++) {
            const input_code = $(`#notebook_grader_test_${test_index}_cases_${case_index}_input_code`).val();
            const output_code = $(`#notebook_grader_test_${test_index}_cases_${case_index}_output_code`).val();
            test_cases.push(_notebook_grader_get_test_case_element(new_test_id, case_index, input_code, output_code));
        }
        const test = {
            "name": $(`#notebook_grader_test_${test_index}_name`).val(),
            "weight": $(`#notebook_grader_test_${test_index}_weight`).val(),
            "setup_code": $(`#notebook_grader_test_${test_index}_setup_code`).val(),
        };
        tests.push(_notebook_grader_get_test_element(new_test_id, test, test_cases));
        delete notebook_grader_tests_cases_count[test_index];
        notebook_grader_tests_cases_count[new_test_id] = test_cases_amount;
        new_test_id++;
    }
    return tests;
}

function _notebook_grader_load_test_case_in_modal(test_case_element) {
    modal_element.find("#notebook_grader_test_cases_container").append(test_case_element);
    $("#notebook_grader_test_cases_header").show();
    $(`#${test_case_element.attr('id')} .form-control`).each(function (index, elem) {
        if (!codeEditors[elem.name])
            registerCodeEditor(elem, $(elem).attr('data-x-language'), $(elem).attr('data-x-lines'));
    });
}

function notebook_grader_on_edit_test(test_id) {
    editing_test_id = test_id;
    const test_data = {
        "name": $(`#notebook_grader_test_${test_id}_name`).val(),
        "weight": $(`#notebook_grader_test_${test_id}_weight`).val(),
        "setup_code": $(`#notebook_grader_test_${test_id}_setup_code`).val(),
    };

    $("#notebook_grader_test_name").val(test_data["name"]);
    $("#notebook_grader_test_weight").val(test_data["weight"]);
    codeEditors["notebook_grader_test_setup_code"].getDoc().setValue(test_data["setup_code"]);
    const test_cases = _notebook_grader_get_test_cases_from_container(test_id, `notebook_grader_test_${test_id}`);
    $.each(test_cases, (case_index, test_case) => {
        _notebook_grader_load_test_case_in_modal(test_case);
    });
    modal_element.modal('show');
}

function notebook_grader_update_test() {
    const test_data = {
        "name": $("#notebook_grader_test_name").val(),
        "weight": $("#notebook_grader_test_weight").val(),
        "setup_code": $("#notebook_grader_test_setup_code").val()
    };
    const test_id = editing_test_id, test_name = test_data["name"],
        test_weight = test_data["weight"], setup_code = test_data["setup_code"];
    const test_cases = _notebook_grader_get_test_cases_from_container(test_id, "notebook_grader_test_cases_container");

    if (!test_name || !test_weight || !test_cases.length) return;

    const test_to_update = $(`#notebook_grader_test_${test_id}`);
    test_to_update.find(`#notebook_grader_test_${test_id}_name`).val(test_name);
    test_to_update.find(`#notebook_grader_test_${test_id}_weight`).val(test_weight);
    test_to_update.find(`#notebook_grader_test_${test_id}_setup_code`).text(setup_code);

    test_to_update.find(`#notebook_grader_test_${test_id}_cases_container`).html("");
    $.each(test_cases, (_, test_case) => {
        test_to_update.find(`#notebook_grader_test_${test_id}_cases_container`).append(test_case);
    });

    modal_element.modal('hide');
    editing_test_id = null;
}

function _clear_modal() {
    $('#notebook_grader_test_form_modal input').val("");
    $('#notebook_grader_test_cases_header').hide();
    $("#notebook_grader_test_cases_container").html("");
    const modal = '#notebook_grader_test_form_modal';
    $(modal + ' .CodeMirror').each(function (i, el) {
        el.CodeMirror.getDoc().setValue("")
    });
}

$("#notebook_grader_submit_test_form").click((e) => {
    e.preventDefault();
    if (editing_test_id !== null) notebook_grader_update_test();
    else notebook_grader_add_test_from_form();
});

modal_element.on("hidden.bs.modal", () => {
    if (editing_test_id !== null) notebook_grader_update_test();
    _clear_modal();
});

modal_element.on("shown.bs.modal", () => {
    const target = '#notebook_grader_test_form_modal';
    $(target + ' .CodeMirror').each(function (i, el) {
        el.CodeMirror.refresh();
    });
});
