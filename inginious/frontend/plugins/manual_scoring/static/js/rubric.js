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
                this.changeCursorToPointerWhenIsOver(matrixField);
                this.changeCursorToDefaultWhenIsOut(matrixField);
            }
        }
    }

    addSelectFunction(matrixField) {
        const self = this;
        this.matrix[matrixField.iIndex][matrixField.jIndex].addEventListener("click", function () {
            const isSelected = self.isSelected(matrixField);
            self.removeSelectionOnRow(matrixField.iIndex);
            if (!isSelected) {
                self.addMarkerClass(matrixField.fieldId);
                self.updateScore(matrixField.jIndex);
            }
        });
    }

    isSelected(matrixField) {
        const fieldSelected = this.getSelectionOnRow(matrixField.iIndex);
        if (!fieldSelected) {
            return false;
        }
        return fieldSelected.fieldId === matrixField.fieldId;
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
        const currentScore = new Score(this.scoreTextId, this.score);
        currentScore.changeColor();
        currentScore.updateScore();
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
        const _this = this;
        const jIndex = 2;
        fieldIds.forEach(function (id) {
                _this.addMarkerClass(id);
                _this.updateScore(parseInt(id[jIndex], 10));
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

class Score {
    constructor(textId, scoreValue) {
        this.text = $(`#${textId}`);
        this.score = scoreValue;
    }

    changeColor() {
        const textColor = this.pickColor(this.score);
        this.text.css("color", textColor);
    }

    updateScore() {
        let currentScore;
        currentScore = parseFloat(this.score).toFixed(1);
        if (isNaN(currentScore))
            currentScore = this.score;
        this.text.html(currentScore);
    }

    pickColor(score) {
        const colorScale = {
            0: "#950000",
            1: "#cc0808",
            2: "#e73509",
            3: "#ff7903",
            4: "#ffb700",
            5: "#ffc800",
            6: "#bfc604",
            7: "#a5d424",
            8: "#67a00c",
            9: "#2d8e00",
            10: "#008e02",
            "defaultColor": "#002a95"
        }

        const id = this.scoreToDictId(score)
        return colorScale[id];
    }

    scoreToDictId(score) {
        let floatScore;
        floatScore = parseFloat(score);
        if (isNaN(floatScore)) {
            return "defaultColor";
        }
        return Math.floor(floatScore * 2);
    }
}