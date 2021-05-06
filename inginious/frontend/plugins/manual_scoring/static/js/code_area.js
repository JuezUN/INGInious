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

const environmentTypes = {
    NOTEBOOK: "notebook_file",
    FILE_MULTI_LANG: "code_file_multiple_languages",
    MULTI_LANG: "code_multiple_languages"
}

class CodeArea {

    constructor(environmentType) {
        this.environmentType = environmentType;
        this.multilangCodeArea = $(`#${CODE_AREA_ID}`);
        this.notebookDiv = $(`#${NOTEBOOK_CODE_AREA_ID}`);
        this.fileDownloadArea = $(`#${FILE_MULTI_LANG_ID}`);
        this.codeMirror = null;
    }

    displayCodeArea() {
        switch (this.environmentType) {
            case environmentTypes.NOTEBOOK:
                this.getNotebookCodeDataAndRender();
                break;
            case environmentTypes.FILE_MULTI_LANG:
                this.showDownloadArea();
                break
            case environmentTypes.MULTI_LANG:
                this.showMultiLangCodeArea();
                this.disabledCodeMirrorEdit();
                break;
            default:
                this.multilangCodeArea = $(`#${this.environmentType}`);
                this.showMultiLangCodeArea();
                break;
        }
    }

    getNotebookCodeDataAndRender() {
        const _this = this;
        $.ajax({
            url: getURLSubmissionCode(),
            method: "GET",
            dataType: "json",
            success: function (data) {
                render_notebook(data, _this.notebookDiv); //Use a external .js file, it's property of multilang plugin
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

    showDownloadArea() {
        this.fileDownloadArea.parent().parent().show();
        this.fileDownloadArea.attr("href",getURLSubmissionCode());
    }

}
