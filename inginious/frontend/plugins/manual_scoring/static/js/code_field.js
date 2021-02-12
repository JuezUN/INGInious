const CODE_AREA_ID = "myTextCode";
const NOTEBOOK_CODE_AREA_ID = "notebook-holder";
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
    constructor() {
        this.environmentType = environmentType();
        this.multilangCodeArea = $(`#${CODE_AREA_ID}`)[0];
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
        $.ajax({
            url: getURLSubmissionCode(),
            method: "GET",
            dataType: "json",
            success: function (data) {
                render_notebook(data, $(`#${NOTEBOOK_CODE_AREA_ID}`)); //Use a external .js file, it's property of multilang plugin
            }
        });
    }

    showMultiLangCodeArea() {
        $("#myTextCodeArea").show();

        const language = LANGUAGES[this.multilangCodeArea.getAttribute("data-language")];
        const myCodeMirror = registerCodeEditor(this.multilangCodeArea, language, 20);

        myCodeMirror.setOption("readOnly", "nocursor");
    }
}
