const LANGUAGES = {
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

class CodeField {
    constructor(multiLangCodeDivId, notebookDivId) {
        this.environmentType = environmentType();
        this.multilangCodeArea = $(`#${multiLangCodeDivId}`);
        this.notebookDiv = $(`#${notebookDivId}`);
        this.displayCodeArea();
    }

    displayCodeArea() {
        if (this.isNotebook()) {
            this.getNotebookCodeDataAndRender();
        } else {
            this.showMultiLangCodeArea();
        }
    }

    isNotebook() {
        return this.environmentType === "Notebook";
    }

    getNotebookCodeDataAndRender() {
        const self = this;
        $.ajax({
            url: getURLSubmissionCode(),
            method: "GET",
            dataType: "json",
            success: function (data) {
                render_notebook(data, self.notebookDiv); //Use a external .js file, it's property of multilang plugin
            }
        });
    }

    showMultiLangCodeArea() {
        this.multilangCodeArea.parent().show();
        const language = LANGUAGES[this.multilangCodeArea.data("language")];
        const myCodeMirror = registerCodeEditor(this.multilangCodeArea.get(0), language, 20);

        myCodeMirror.setOption("readOnly", "nocursor");
    }
}
