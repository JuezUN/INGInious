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
            url: getURLSubmissionCode(),
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
