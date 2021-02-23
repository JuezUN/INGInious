const LANGUAGES = {
    "java7": "java",
    "java8": "java",
    "cpp": "cpp",
    "cpp11": "cpp",
    "c": "c",
    "c11": "c",
    "python3": "python",
    "vhdl": "vhdl",
    "verilog": "verilog",
    "rst": "rst"
};

class CodeArea {

    constructor(multiLangCodeDivId, notebookDivId = null, environmentType = "") {
        this.environmentType = environmentType
        this.multilangCodeArea = $(`#${multiLangCodeDivId}`);
        this.codeMirror = null;
        if (notebookDivId)
            this.notebookDiv = $(`#${notebookDivId}`);
    }

    displayCodeArea() {
        if (this.isNotebook()) {
            this.getNotebookCodeDataAndRender();
        } else {
            this.showMultiLangCodeArea();
            this.disabledCodeMirrorEdit();
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
        this.codeMirror = registerCodeEditor(this.multilangCodeArea.get(0), language, 20);
    }

    disabledCodeMirrorEdit() {
        this.codeMirror.setOption("readOnly", "nocursor");
    }

}
