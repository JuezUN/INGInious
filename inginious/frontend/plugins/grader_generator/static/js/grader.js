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
    const idPrefix = getIdPrefix();
    const parameters = getParametersArray();
    const buttons = getButtons();

    const baseOldId = `${idPrefix}_${itemId}`
    const baseNewId = `${idPrefix}_${newPos}`;
    const newNameAttrPrefix = `${idPrefix}[${newPos}]`;


    $.each(parameters, (_, parameterId) => {
        let parameter = $(`#${baseOldId}_${parameterId}`);
        parameter.attr("id", `${baseNewId}_${parameterId}`);
        parameter.attr("name", `${newNameAttrPrefix}[${parameterId}]`)
    });

    $.each(buttons, (_, button) => {
        let buttonId = button.buttonId;
        let functionName = button.functionName;
        let buttonParameter = $(`#${baseOldId}_${buttonId}`);
        buttonParameter.attr("id", `${baseNewId}_${buttonId}`)
        buttonParameter.attr("onclick", `${functionName}(${newPos})`)
    });

    if (isNotebook) {
    }

    $(`#${baseOldId}`).attr("id", baseNewId);


}

function getContainerDiv() {
    if (isNotebook) {
        return $("#notebook_grader_tests_container")[0];
    } else {
        return $("#grader_test_cases_container")[0];
    }
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