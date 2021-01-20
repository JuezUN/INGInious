const languages = {
    "java7": "java",
    "java8": "java",
    "cpp": "cpp",
    "cpp11": "cpp",
    "c": "c",
    "c11": "c",
    "python3": "python",
    "vhdl": "vhdl",
    "verilog": "verilog"
};

class RubricScoring {
    constructor() {
        this.score = 0.0;
        this.matrix = [];
        this.matrixLength = 5;
        this.classMarkerId = "box1";
        this.scoreTextId = "output";
        this.formMatrixRespectRubric();
        this.addListeners();
    }

    removeMarkerClass(fieldId) {
        document.getElementById(fieldId).classList.remove(this.classMarkerId);
    }

    addMarkerClass(fieldId) {
        document.getElementById(fieldId).classList.add(this.classMarkerId);
    }

    isFieldSelected(matrixField) {
        return this.matrix[matrixField.iIndex][matrixField.jIndex].classList.contains(this.classMarkerId);
    }

    removeSelectionOnRow(row) {
        for (let i = 0; i < this.matrixLength; i++) {
            let matrixField = new MatrixField(row, i);
            if (this.isFieldSelected(matrixField)) {
                this.removeMarkerClass(matrixField.fieldId);
                this.updateScore(i, false);
                break;
            }
        }
    }

    updateScoreText() {
        document.getElementById(this.scoreTextId).innerHTML = "Current Score: " + this.score.toFixed(1);
    }

    addListeners() {
        for (let i = 0; i < this.matrixLength; i++) {
            for (let j = 0; j < this.matrixLength; j++) {
                let matrixField = new MatrixField(i, j);
                this.addSelectFunction(matrixField);
                this.addDeselectFunction(matrixField);
                this.changeCursorToDefaultWhenIsOut(matrixField);
                this.changeCursorToPointerWhenIsOver(matrixField);
            }
        }
    }

    addSelectFunction(matrixField) {
        const self = this;
        this.matrix[matrixField.iIndex][matrixField.jIndex].addEventListener("click", function () {
            self.removeSelectionOnRow(matrixField.iIndex);
            self.addMarkerClass(matrixField.fieldId);
            self.updateScore(matrixField.jIndex);
        });
    }

    updateScore(colPosition, isAdd = true) {
        if (isAdd) {
            this.score += (colPosition + 1) * 0.2;
        } else {
            this.score -= (colPosition + 1) * 0.2;
        }
        this.updateScoreText();
    }

    addDeselectFunction(matrixField) {
        const self = this;
        this.matrix[matrixField.iIndex][matrixField.jIndex].addEventListener("dblclick", function () {
            self.removeMarkerClass(matrixField.fieldId);
            self.updateScore(matrixField.jIndex, false);
        });
    }

    changeCursorToPointerWhenIsOver(matrixField) {
        this.matrix[matrixField.iIndex][matrixField.jIndex].addEventListener("mouseover", function () {
            document.body.style.cursor = "pointer";
        });
    }

    changeCursorToDefaultWhenIsOut(matrixField) {
        this.matrix[matrixField.iIndex][matrixField.jIndex].addEventListener("mouseout", function () {
            document.body.style.cursor = "default";
        });
    }

    formMatrixRespectRubric() {
        for (let i = 0; i < this.matrixLength; i++) {
            this.matrix[i] = [];
            for (let j = 0; j < this.matrixLength; j++) {
                let matrixField = new MatrixField(i, j);
                this.matrix[i][j] = document.getElementById(matrixField.fieldId);
            }
        }
    }
}

class MatrixField {
    constructor(iIndex, jIndex) {
        this.iIndex = iIndex;
        this.jIndex = jIndex;
    }

    get fieldId() {
        return `${this.iIndex}-${this.jIndex}`;
    }
}

class MessageBox {
    constructor(divId, textContent, type, dismissible = true) {
        this.divElement = document.getElementById(divId);
        this.textContent = textContent;
        this.type = type;
        this.dismissible = dismissible;
        this.generateHtmlCode();
        this.displayBoxMessage();
    }

    displayBoxMessage() {
        this.divElement.innerHTML += this.code;
        this.divElement.style.display = "block";
        if (this.dismissible) {
            this.doDisappearEffect();
        }
    }

    doDisappearEffect() {
        let opacity = 1;
        const element = this.divElement;
        const timer = setInterval(function () {
            if (opacity <= 0.1) {
                element.style.display = "none";
                clearInterval(timer);
                element.innerHTML = "";
            }
            element.style.opacity = opacity;
            element.style.filter = "alpha(opacity=" + opacity * 100 + ")";
            opacity -= opacity * 0.05;
        }, 100);
    }

    generateHtmlCode() {
        let code = '<div class="alert fade in ';
        if (this.dismissible)
            code += 'alert-dismissible ';
        code += 'alert-' + this.type + '" role="alert">';
        if (this.dismissible)
            code += '<button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>';
        code += this.textContent;
        code += '</div>';
        this.code = code;
    }

}

function commentSubmit() {
    const txtComment = document.getElementById("text_comment");
    const contentInfo = "Successfully saved";
    const contentDanger = "Error at saving Comment, please try again."
    const contentWarning = "Error at saving Comment, comment to long, max length of comment is 1000."
    const maxTam = 1000;

    if (txtComment.value.length > maxTam) {
        const message = new MessageBox("grade_edit_submit_status", contentWarning, "warning");
        return;
    }

    jQuery.ajax({
        success: function (data) {
            const message = new MessageBox("grade_edit_submit_status", contentInfo, "info");
        },
        method: "POST",

        data: {"comment": txtComment.value},

        error: function (request, status, error) {
            const message = new MessageBox("grade_edit_submit_status", contentDanger, "danger");
        }
    });
}

function save(rubric) {
    let contentInfo = "Submission graded and stored";
    let contentDanger = "Something went wrong";
    jQuery.ajax({
        success: function (data) {
            commentSubmit();
            const message = new MessageBox("grade_edit_submit_status", contentInfo, "info");
        },
        method: "POST",

        data: {"grade": rubric.score},

        error: function (request, status, error) {
            const message = new MessageBox("grade_edit_submit_status", contentDanger, "danger");
        }
    });
}

function loadFeedBack() {
    const feedbackContent = getHtmlCodeForFeedBack();
    const feedbackType = getTextBoxTypeBaseOnResult();
    new MessageBox("task_alert", feedbackContent, feedbackType, false);
}

class CodeField {
    constructor() {
        this.environmentType = environmentType();
        this.multilangCodeArea = $("#myTextCode")[0];
        this.displayCodeArea();
    }

    displayCodeArea() {
        if (this.isNotebook()) {
            this.getNotebookCodeDataAndRender();
        } else {
            this.showMultiLangCodeArea()
        }
    }

    isNotebook() {
        return this.environmentType === "Notebook";
    }

    getNotebookCodeDataAndRender() {
        $.ajax({
            url: getUrlToGetCode(),
            method: "GET",
            dataType: "json",
            success: function (data) {
                render_notebook(data); //Use a external .js file, it's property of multilang plugin
            }
        });
    }

    showMultiLangCodeArea() {
        $("#myTextCodeArea").show();

        const language = languages[this.multilangCodeArea.getAttribute("data-language")];
        const myCodeMirror = registerCodeEditor(this.multilangCodeArea, language, 20);

        myCodeMirror.setOption("readOnly", "nocursor");
    }
}

function addToggleBehaviorToProblemDescription() {
    $("#info").click(function () {
        $("#text-context").collapse("toggle");
    });
}

function addSaveFunctionToSaveButton(rubric) {
    $("#save_button").click(function () {
        save(rubric);
    })
}


jQuery(document).ready(function () {
    new CodeField();
    const rubric = new RubricScoring();
    addToggleBehaviorToProblemDescription();
    loadFeedBack();
    addSaveFunctionToSaveButton(rubric);

    window.save = save;
});



