const isNotebook = $("#environment").val() === "Notebook";

class Button {
    constructor(buttonId, functionName) {
        this.buttonId = buttonId;
        this.functionName = functionName;
    }
}

function studio_load_grader_test_cases(test_cases) {
    if (isNotebook) {
        notebook_grader_load_all_tests(test_cases);
    } else {
        multiLangLoadAllTests(test_cases);
    }
}

function activeSortableMode() {
    const testCases = getContainerDiv();

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

function getContainerDiv() {
    if (isNotebook) {
        return $("#notebook_grader_tests_container")[0];
    } else {
        return $("#grader_test_cases_container")[0];
    }
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

function updateItemIds(itemId, newId) {

    updateRowId(itemId, newId);
    updateParametersId(itemId, newId);
    updateButtonsId(itemId, newId);

    if (isNotebook) {
        updateTestCasesContainer(itemId, newId);
    }


}


function updateRowId(itemId, newId) {
    const baseOldId = getBaseId(itemId);
    const baseNewId = getBaseId(newId);

    $(`#${baseOldId}`).attr("id", baseNewId);
}

function updateParametersId(itemId, newId) {
    const parameters = getParametersArray();
    const newNameAttrPrefix = `${getIdPrefix()}[${newId}]`;
    const baseOldId = getBaseId(itemId);
    const baseNewId = getBaseId(newId);

    $.each(parameters, (_, parameterId) => {
        let parameter = $(`#${baseOldId}_${parameterId}`);
        parameter.attr("id", `${baseNewId}_${parameterId}`);
        parameter.attr("name", `${newNameAttrPrefix}[${parameterId}]`)
    });

}

function updateButtonsId(itemId, newId) {
    const baseOldId = getBaseId(itemId);
    const baseNewId = getBaseId(newId);
    const buttons = getButtons();

    $.each(buttons, (_, button) => {
        let buttonId = button.buttonId;
        let functionName = button.functionName;
        let buttonParameter = $(`#${baseOldId}_${buttonId}`);
        buttonParameter.attr("id", `${baseNewId}_${buttonId}`);
        buttonParameter.attr("onclick", `${functionName}(${newId})`);
    });

}

function getBaseId(id) {
    return `${getIdPrefix()}_${id}`;
}

function getIdPrefix() {
    if (isNotebook) {
        return "notebook_grader_test";
    } else {
        return "grader_test_cases"
    }
}

function getParametersArray() {
    if (isNotebook) {
        return notebookTestCaseParameterIds;
    } else {
        return multiLangTestCaseParameters;
    }
}

function getButtons() {
    if (isNotebook) {
        return notebookButtons;
    } else {
        return multiLangButtons;
    }
}


function updateTestCasesContainer(itemId, newId) {
    const numOfCases = getCurrentNumTestCases(itemId);
    const baseOldId = getBaseId(itemId);
    const baseNewId = getBaseId(newId);
    const newNameAttrPrefix = `${getIdPrefix()}[${newId}]`;

    $(`#${baseOldId}_cases_container`).attr("id", `${baseNewId}_cases_container`);
    for (let i = 0; i < numOfCases; i++) {
        $(`#${baseOldId}_cases_${i}`).attr("id", `${baseNewId}_cases_${i}`);
        $.each(notebookModalParameterIds, (_, parameterId) => {
            let parameter = $(`#${baseOldId}_cases_${i}_${parameterId}`);
            parameter.attr("id", `${baseNewId}_cases_${i}_${parameterId}`);
            parameter.attr("name", `${newNameAttrPrefix}[cases][${i}][${parameterId}]`);
        });
        $.each(notebookModalButtonIds, (_, button) => {
            let buttonId = button.buttonId;
            let functionName = button.functionName;
            let buttonParameter = $(`#${baseOldId}_cases_${i}_${buttonId}`);
            buttonParameter.attr("onclick", `${functionName}(${newId},${i})`);
            buttonParameter.attr("id", `${baseNewId}_cases_${i}_${buttonId}`);
        });
    }

}

function toggle_selection_tests_cases() {
    const checkboxButton = getDiffCheckboxButton();
    const option = !checkboxButton[0].checked;
    // Activate in case of button press and not checkbox
    checkboxButton.prop("checked", option);
    changeSelectionTestCases(option);

}

function changeSelectionTestCases(option) {
    const numTests = getCurrentNumTests();
    for (let i = 0; i < numTests; i++) {
        $(`#${getIdPrefix()}_${i}_${getDiffIdSuffix()}`).prop("checked", option);
    }
}

function isAllShowDiffChecked() {
    const numListChecked = $(`[id$='${getDiffIdSuffix()}']:checked`).length;
    return getCurrentNumTests() === numListChecked;
}

function checkDiffStatus() {
    const checkboxButton = getDiffCheckboxButton();
    if (isAllShowDiffChecked()) {
        checkboxButton.prop("checked", true);
    } else {
        checkboxButton.prop("checked", false);
    }
}

function getDiffCheckboxButton() {
    if (isNotebook) {
        return $("#notebookToggleSelectTestCases");
    } else {
        return $("#toggle_select_test_cases");
    }
}

function getDiffIdSuffix() {
    if (isNotebook) {
        return "show_debug_info";
    } else {
        return "diff_shown";
    }
}

function getCurrentNumTests() {
    if (isNotebook) {
        return notebook_grader_tests_sequence;
    } else {
        return grader_test_cases_count;
    }
}

$("[href='#tab_grader']").click(function () {
    checkDiffStatus();
});
