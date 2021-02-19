class Rubric {
    constructor() {
        this.score = 0.0;
        this.matrix = [];
        this.matrixLength = 5;
        this.classMarkerId = "box1";
        this.scoreTextId = "output";
        this.formMatrixRespectRubric();
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

    makeRubricInteractive() {
        for (let i = 0; i < this.matrixLength; i++) {
            for (let j = 0; j < this.matrixLength; j++) {
                let matrixField = new MatrixField(i, j);
                this.addSelectFunction(matrixField);
                this.addDeselectFunction(matrixField);
                this.changeCursorToPointerWhenIsOver(matrixField);
                this.changeCursorToDefaultWhenIsOut(matrixField);
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

    removeSelectionOnRow(row) {
        let matrixField = this.getSelectionOnRow(row);
        if (matrixField !== null) {
            this.removeMarkerClass(matrixField.fieldId);
            this.updateScore(matrixField.jIndex, false);
        }
    }

    getSelectionOnRow(row) {
        for (let i = 0; i < this.matrixLength; i++) {
            let matrixField = new MatrixField(row, i);
            if (this.isFieldSelected(matrixField)) {
                return matrixField;
            }
        }
        return null;
    }

    addMarkerClass(fieldId) {
        document.getElementById(fieldId).classList.add(this.classMarkerId);
    }

    removeMarkerClass(fieldId) {
        document.getElementById(fieldId).classList.remove(this.classMarkerId);
    }


    isFieldSelected(matrixField) {
        return this.matrix[matrixField.iIndex][matrixField.jIndex].classList.contains(this.classMarkerId);
    }


    updateScoreText() {
        document.getElementById(this.scoreTextId).innerHTML = this.score.toFixed(1);
    }


    updateScore(colPosition, isAdd = true) {
        if (isAdd) {
            this.score += (colPosition + 1) * 0.2;
        } else {
            this.score -= (colPosition + 1) * 0.2;
        }
        this.updateScoreText();
    }

    getSelectedFieldIds() {
        let fieldIds = [];
        for (let i = 0; i < this.matrixLength; i++) {
            let matrixField = this.getSelectionOnRow(i);
            if (matrixField !== null) {
                fieldIds.push(matrixField.fieldId);
            }
        }
        return fieldIds;
    }

    loadSelectedFields(fieldIds) {
        const self = this;
        const jIndex = 2;
        fieldIds.forEach(function (id) {
                self.addMarkerClass(id);
                self.updateScore(parseInt(id[jIndex],10));
            }
        );
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