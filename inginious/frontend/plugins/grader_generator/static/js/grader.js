const environment =  $("#environment");
const isNotebook = environment.val() === "Notebook";
const isMultiLang = environment.val() === "multiple_languages";
const isDataScience = environment.val() === "Data Science";

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
    /*It uses a library named SortableJS. The parameters are:
    * group: it's just a name in this case
    * animation: It's to give a animation effect whit 150ms
    * easing: it's a function who complements the animation behavior
    * handle: it takes a selector to indicate what elements are the only who can be grabbed
    * chosenClass: it adds a CSS class when a item has been chose
    * onEnd: it defines a behavior when the user ends to move a item*/
    const testCases = getContainerDiv();

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
    /*Depending of where the test will be moved,
    * it's just necessary update a few test ids*/
    const itemPosIncreased = (oldPos - newPos) < 0;
    if (itemPosIncreased) {
        updateIdsLowestToHighest(oldPos, newPos);
    } else {
        updateIdsHighestToLowest(oldPos, newPos);
    }

}

function updateIdsHighestToLowest(oldPos, newPos) {
    const auxName = "AUX"
    updateTestInternalIds(oldPos, auxName);
    for (let i = oldPos - 1; i >= newPos; i--) {
        updateTestInternalIds(i, i + 1);
    }
    updateTestInternalIds(auxName, newPos)

}

function updateIdsLowestToHighest(oldPos, newPos) {
    const auxName = "AUX"
    updateTestInternalIds(oldPos, auxName);
    for (let i = oldPos + 1; i <= newPos; i++) {
        updateTestInternalIds(i, i - 1);
    }
    updateTestInternalIds(auxName, newPos)

}

function updateTestInternalIds(itemId, newId) {

    updateTestRowId(itemId, newId);
    updateTestParametersId(itemId, newId);
    updateButtonsId(itemId, newId);

    if (isNotebook) {
        updateNotebookTestCasesContainer(itemId, newId);
    }


}

function updateTestRowId(itemId, newId) {
    const baseOldId = getBaseId(itemId);
    const baseNewId = getBaseId(newId);

    $(`#${baseOldId}`).attr("id", baseNewId);
}

function updateTestParametersId(itemId, newId) {
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
    const buttons = getButtonsInfo();

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

function getButtonsInfo() {
    if (isNotebook) {
        return notebookButtons;
    } else {
        return multiLangButtons;
    }
}


function updateNotebookTestCasesContainer(itemId, newId) {
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

function toggleSelectionTestsCases() {
    const checkboxButton = getDiffCheckboxButton();
    const option = !checkboxButton[0].checked;
    checkboxButton.prop("checked", option);
    setAllDiffShowCheckboxValue(option);

}

function setAllDiffShowCheckboxValue(option) {
    const numTests = getCurrentNumTests();
    for (let i = 0; i < numTests; i++) {
        $(`#${getIdPrefix()}_${i}_${getDiffIdSuffix()}`).prop("checked", option);
    }
}

function isAllShowDiffChecked() {
    const numListChecked = $(`[id$='${getDiffIdSuffix()}']:checked`).length;
    return getCurrentNumTests() === numListChecked;
}

function updateMainShowDiffsCheckbox() {
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
    updateMainShowDiffsCheckbox();
});
