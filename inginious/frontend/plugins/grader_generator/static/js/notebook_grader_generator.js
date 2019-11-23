let notebook_grader_tests_sequence = 0;
let notebook_grader_tests = {};
let editing_test_id = null;
// let test_cases_input = [];
// let ids_test_cases_input = [];

function add_notebook_test_case_from_form() {
    add_notebook_test_case({
        "input_code": $("#grader_test_case_input_code").val(),
        "output_code": $("#grader_test_cases_output_code").val()
    });
}

function add_notebook_test_case(test_case) {
    test_case = $.extend({
        "input_code": null,
        "output_code": null
    }, test_case);

    const test_id = editing_test_id || notebook_grader_tests_sequence;

    const case_id = notebook_grader_tests[test_id],
        inputCode = test_case["input_code"],
        outputCode = test_case["output_code"];

    if (!notebook_grader_tests[test_id]) {
        notebook_grader_tests[test_id] = 0;
    }

    if (!inputCode || !outputCode) return;

    let templateElement = _get_test_case_html(test_id, case_id, inputCode, outputCode);

    notebook_grader_tests[test_id]++;

    const first_row = (notebook_grader_tests[test_id] === 1);

    if (first_row) {
        $('#notebook_grader_test_cases_header').show();
    }

    $('#notebook_grader_test_cases_container').append(templateElement);
    $("#grader_test_case_input_code").val("");
    $("#grader_test_cases_output_code").val("");
}

function load_notebook_test_case(test_id, case_index, test_data) {
    test_data = $.extend({
        "input_code": null,
        "output_code": null
    }, test_data);

    // if (!notebook_grader_tests[test_id]) {
    //     notebook_grader_tests[test_id] = 0;
    // }

    const case_id = case_index,
        inputCode = test_data["input_code"],
        outputCode = test_data["output_code"];

    if (!inputCode || !outputCode) return;

    let templateElement = _get_test_case_html(test_id, case_id, inputCode, outputCode);

    // notebook_grader_tests[test_id]++;
    // notebook_grader_test_cases_count++;

    // const first_row = (notebook_grader_test_cases_count === 1);

    // if (first_row) {
    // }
    $('#notebook_grader_test_cases_header').show();

    $('#notebook_grader_test_cases_container').append(templateElement);
}

function notebook_remove_test_case(test_id, case_id) {
    $(`#notebook_grader_test_cases_${test_id}_${case_id}`).remove();
    notebook_grader_tests[test_id]--;
    if (notebook_grader_tests[test_id] === 0) {
        $('#notebook_grader_test_cases_header').hide();
    }
    // let ind_of_test_case = ids_test_cases_input.findIndex(el => el === id);
    // test_cases_input.splice(ind_of_test_case, 1);
    // ids_test_cases_input.splice(ind_of_test_case, 1);
}

function _get_test_case_html(test_id, case_id, input_code, output_code) {
    const template = $("#notebook_test_case_template").html().replace(/TID/g, test_id).replace(/CID/g, case_id);

    const templateElement = $(template);
    templateElement.find(`#notebook_grader_test_cases_${test_id}_${case_id}_input_code`).text(input_code);
    templateElement.find(`#notebook_grader_test_cases_${test_id}_${case_id}_output_code`).text(output_code);
    return templateElement;
}

function _get_test_cases(test_id, from_container) {
    const amount_cases = notebook_grader_tests[test_id];
    const test_cases_element = $(`#${from_container}`);
    const test_cases = [];
    for (let case_id = 0; case_id < amount_cases; case_id++) {
        const case_element = test_cases_element.find(`#notebook_grader_test_cases_${test_id}_${case_id}`);
        test_cases.push(case_element);
    }
    return test_cases;
}

function add_notebook_test_from_form() {
    add_notebook_test({
        "name": $("#notebook_test_name").val(),
        "weight": $("#notebook_test_weight").val(),
        "setup_code": $("#notebook_test_setup_code").val()
    });
}

function notebook_load_grader_tests(tests) {
    $.each(tests, function (test_index, test) {
        $.each(test["cases"], (case_index, test_case) => {
            add_notebook_test_case({
                "input_code": test_case["input_code"],
                "output_code": test_case["output_code"]
            });
        });
        add_notebook_test(test, test["cases"].length);
    });
}

function add_notebook_test(test_data, cases_amount = 0) {
    test_data = $.extend({
        "name": "test",
        "weight": 1.0,
        "setup_code": "",
    }, test_data);

    const test_id = notebook_grader_tests_sequence, test_name = test_data["name"],
        test_weight = test_data["weight"], setup_code = test_data["setup_code"];

    if (!notebook_grader_tests[test_id]) {
        notebook_grader_tests[test_id] = cases_amount;
    }
    const test_cases = _get_test_cases(test_id, "notebook_grader_test_cases_container");

    if (!test_name || !test_weight || !test_cases.length) return;

    const template = $("#notebook_grader_test_template").html().replace(/TID/g, test_id);

    const templateElement = $(template);
    templateElement.find(`#notebook_grader_test_${test_id}_name`).val(test_name);
    templateElement.find(`#notebook_grader_test_${test_id}_weight`).val(test_weight);
    templateElement.find(`#notebook_grader_test_${test_id}_setup_code`).text(setup_code);

    $.each(test_cases, (_, test_case) => {
        templateElement.find(`#notebook_test_cases_${test_id}_container`).append(test_case);
    });

    notebook_grader_tests_sequence++;
    // notebook_grader_test_cases_count++;
    // test_cases_input.push(inputCode);
    // ids_test_cases_input.push(test_id)

    const first_row = (notebook_grader_tests_sequence === 1);

    if (first_row) {
        $('#notebook_grader_tests_header').show();
    }

    $('#notebook_grader_tests_container').append(templateElement);
    $("#notebook_grader_add_test_case_modal").modal('hide');
}

function _clear_modal() {
    $('#notebook_grader_add_test_case_modal input').val("");
    $('#notebook_grader_add_test_case_modal textarea').val("");
    $('#notebook_grader_test_cases_header').hide();
    $("#notebook_grader_test_cases_container").html("");
}

function notebook_grader_remove_test(test_id) {
    $(`#notebook_grader_test_${test_id}`).remove();
    delete notebook_grader_tests[test_id];
    notebook_grader_tests_sequence--;
    if (notebook_grader_tests_sequence === 0) {
        $('#notebook_grader_tests_header').hide();
    }
}

function notebook_grader_edit_test(test_id) {
    editing_test_id = test_id;
    const test_data = {
        "name": $(`#notebook_grader_test_${test_id}_name`).val(),
        "weight": $(`#notebook_grader_test_${test_id}_weight`).val(),
        "setup_code": $(`#notebook_grader_test_${test_id}_setup_code`).val(),
    };

    $("#notebook_test_name").val(test_data["name"]);
    $("#notebook_test_weight").val(test_data["weight"]);
    $("#notebook_test_setup_code").val(test_data["setup_code"]);
    const test_cases = _get_test_cases(test_id, `notebook_grader_test_${test_id}`);
    $.each(test_cases, (case_index, test_case) => {
        const input_code = $(`#notebook_grader_test_cases_${test_id}_${case_index}_input_code`).val();
        const output_code = $(`#notebook_grader_test_cases_${test_id}_${case_index}_output_code`).val();
        load_notebook_test_case(test_id, case_index, {input_code, case_index, output_code});
    });
    $("#notebook_grader_add_test_case_modal").modal('show');
}

function update_notebook_test(test_data) {
   test_data = $.extend({
        "name": "test",
        "weight": 1.0,
        "setup_code": "",
    }, test_data);

    const test_id = editing_test_id, test_name = test_data["name"],
        test_weight = test_data["weight"], setup_code = test_data["setup_code"];

    const test_cases = _get_test_cases(test_id, "notebook_grader_test_cases_container");

    if (!test_name || !test_weight || !test_cases.length) return;


    const test_to_update = $(`#notebook_grader_test_${test_id}`);
    test_to_update.find(`#notebook_grader_test_${test_id}_name`).val(test_name);
    test_to_update.find(`#notebook_grader_test_${test_id}_weight`).val(test_weight);
    test_to_update.find(`#notebook_grader_test_${test_id}_setup_code`).text(setup_code);

    test_to_update.find(`#notebook_test_cases_${test_id}_container`).html("");
    $.each(test_cases, (_, test_case) => {
        test_to_update.find(`#notebook_test_cases_${test_id}_container`).append(test_case);
    });

    // $('#notebook_grader_tests_container').append(test_to_update);
    $("#notebook_grader_add_test_case_modal").modal('hide');
    editing_test_id = null;
}

$("#submit_notebook_test_form").click((e) => {
    e.preventDefault();
   if(editing_test_id !== null) update_notebook_test({
       "name": $("#notebook_test_name").val(),
        "weight": $("#notebook_test_weight").val(),
        "setup_code": $("#notebook_test_setup_code").val()
   });
   else add_notebook_test_from_form();
});

$("#notebook_grader_add_test_case_modal").on("hidden.bs.modal", () => {
    _clear_modal();
});
