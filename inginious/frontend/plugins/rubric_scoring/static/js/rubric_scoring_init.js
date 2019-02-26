let score = 0.0;
let matrix = [];

//Add or delete the class
function removeClass(id) {
    document.getElementById(id).classList.remove("box1");
}

function addClass(id) {
    document.getElementById(id).classList.add("box1");
}


function removeSelectionOnRow(row) {
    for (let i = 0; i < 5; i++) {
        if (matrix[row][i].classList.contains("box1")) {
            removeClass(`${row}-${i}`);
            score -= (i + 1) * 0.2;
            break;
        }
    }
}

function updateScore() {
    document.getElementById("output").innerHTML = "Current Score: " + score.toFixed(1);
}

/* Save the grade and comments */

//Show an alert with save process result
function displayTaskSubmitMessageRubric(content, type, dismissible) {
    let code = getAlertCode(content, type, dismissible);
    let element = document.getElementById("grade_edit_submit_status");
    document.getElementById("grade_edit_submit_status").innerHTML = code;
    element.style.display = "block";
    if (dismissible) {
        let op = 1;  // initial opacity
        let timer = setInterval(function () {
            if (op <= 0.1) {
                clearInterval(timer);
                element.style.display = "none";

            }
            element.style.opacity = op;
            element.style.filter = "alpha(opacity=" + op * 100 + ")";
            op -= op * 0.05;
        }, 50);

    }
}

function save() {
    let contentInfo = "Submission graded and stored";
    let contentDanger = "Something went wrong";
    jQuery.ajax({
        success: function (data) {
            commentSubmit();
            displayTaskSubmitMessageRubric(contentInfo, "info", true);
        },
        method: "POST",

        data: {"grade": score},

        error: function (request, status, error) {
            displayTaskSubmitMessageRubric(contentDanger, "danger", true);
        }
    });
}

function commentSubmit() {
    let txt_comment = document.getElementById("text_comment");
    let content_info = "Successfully saved";
    let content_danger = "Error at saving Comment, please try again."
    let content_warning = "Error at saving Comment, comment to long, max length of comment is 1000."
    let maxTam = 1000;

    if (txt_comment.value.length > maxTam) {
        displayTaskSubmitMessageRubric(content_warning, "warning", true);
        return;
    }
    // alert(txt_comment.value);

    jQuery.ajax({
        success: function (data) {
            displayTaskSubmitMessageRubric(content_info, "info", true);
        },
        method: "POST",

        data: {"comment": txt_comment.value},

        error: function (request, status, error) {
            displayTaskSubmitMessageRubric(content_danger, "danger", true);
        }
    });
}

jQuery(document).ready(function () {
    if (document.location.href.match(/submission/)) {
        /*===========================================
        *                Code frame
        * Display the submission's code
        * There are two types of code: multi language and Notebook
        * ===========================================*/
        //Dictionary of Languages for codemirror
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
        //Set code frame
        if (environment() === "Notebook") {
            //Get notebook data
            $.ajax({
                url: urlRequest(),
                method: "GET",
                dataType: "json",
                success: function (data) {
                    render_notebook(data); //Use a external .js file, it's property of multilang plugin
                }
            });
        } else {
            //Case if it is code. use code Mirror
            const textArea = $("#myTextCode")[0];
            $("#myTextCodeArea").show();
            const language = languages[textArea.getAttribute("data-language")];
            const myCodeMirror = registerCodeEditor(textArea, language, 20);
            myCodeMirror.setOption("readOnly", "nocursor");
        }


        //Add click functionality for problem title. It "toggle" the problem description text
        $("#info").click(function () {
            $("#text-context").collapse("toggle");
        });


        /* =======================================================
        *                     Rubric configuration
        * This work by add and delete a class named box1 that change the background of the square inside oh table
        * That class is used to identify the selected fields
        * =========================================================*/
        //Add listeners to squares
        for (let i = 0; i < 5; i++) {
            matrix[i] = [];
            for (let j = 0; j < 5; j++) {
                matrix[i][j] = document.getElementById(i + "-" + j);
                //Add function
                matrix[i][j].addEventListener("click", function () {
                    removeSelectionOnRow(i);
                    addClass(i + "-" + j);
                    score += (j + 1) * 0.2;
                    updateScore();
                });
                matrix[i][j].addEventListener("dblclick", function () {
                    removeClass(i + "-" + j);
                    score -= (j + 1) * 0.2;
                    updateScore();
                });
                //Static, just change the cursor
                matrix[i][j].addEventListener('mouseover', function () {
                    document.body.style.cursor = "pointer";
                });
                matrix[i][j].addEventListener('mouseout', function () {
                    document.body.style.cursor = "default";
                });
            }
        }


        window.save = save;
    }

    /* =========================
    *  Show the feedback cards about the submissions
    * ========================== */
    loadFeedbackCode();

});



