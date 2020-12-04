jQuery(document).ready(function () {
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


    let textArea = document.getElementById("myTextCode")
    let score = 0.0;
    let language = languages[textArea.getAttribute('data-language')];
    let myCodeMirror = registerCodeEditor(textArea, language, 20);
    myCodeMirror.setOption("readOnly", "nocursor");

    let matrix = [];
//Add listeners to squares
    for (let i = 0; i < 5; i++) {
        matrix[i] = [];
        for (let j = 0; j < 5; j++) {
            matrix[i][j] = document.getElementById(i + "-" + j);
            //Add function
            matrix[i][j].addEventListener('click', function () {
                removeSelectionOnRow(i);
                addClass(i + "-" + j);
                score += (j + 1) * 0.2;
                updateScore();
            });
            matrix[i][j].addEventListener('dblclick', function () {
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

    function removeClass(id) {
        document.getElementById(id).classList.remove("box1");
    }

    function addClass(id) {
        document.getElementById(id).classList.add("box1");
    }

//
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

    function save() {
        let content_info = "Submission graded and stored";
        let content_danger = "Something went wrong";
        jQuery.ajax({
            success: function (data) {
                comment_submit();
                studio_display_task_submit_message_rubric(content_info, "info", true);
            },
            method: "POST",

            data: {"grade": score},

            error: function (request, status, error) {
                studio_display_task_submit_message_rubric(content_danger, "danger", true);
            }
        });
    }

    function comment_submit() {
        let txt_comment = document.getElementById("text_comment");
        let content_info = "Successfully saved";
        let content_danger = "Error at saving Comment, please try again."
        let content_warning = "Error at saving Comment, comment to long, max length of comment is 1000."
        let maxTam = 1000;

        if (txt_comment.value.length > maxTam) {
            studio_display_task_submit_message_rubric(content_warning, "warning", true);
            return;
        }
        // alert(txt_comment.value);

        jQuery.ajax({
            success: function (data) {
                studio_display_task_submit_message_rubric(content_info, "info", true);
            },
            method: "POST",

            data: {"comment": txt_comment.value},

            error: function (request, status, error) {
                studio_display_task_submit_message_rubric(content_danger, "danger", true);
            }
        });
    }

    function studio_display_task_submit_message_rubric(content, type, dismissible) {
        let code = getAlertCode(content, type, dismissible);
        let element = document.getElementById('grade_edit_submit_status');
        document.getElementById('grade_edit_submit_status').innerHTML = code;
        element.style.display = 'block';
        if (dismissible) {
            let op = 1;  // initial opacity
            let timer = setInterval(function () {
                if (op <= 0.1) {
                    clearInterval(timer);
                    element.style.display = 'none';

                }
                element.style.opacity = op;
                element.style.filter = 'alpha(opacity=' + op * 100 + ")";
                op -= op * 0.05;
            }, 50);

        }
    }

    window.save = save;
});



