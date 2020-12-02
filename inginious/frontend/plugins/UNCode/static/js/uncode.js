jQuery(document).ready(function () {

    function updateNavbarLogo(imagePath) {
        let logoElement = $('#wrapper')
            .find('> div.navbar.navbar-default.navbar-static-top > div > div.navbar-header > a');
        const image = logoElement.find("> img").attr("src", imagePath);
        logoElement.text("");
        logoElement.html(image).append(" Code");
    }

    function updateFooter() {
        // Update footer with new information.
        const footer = $("#footer");
        footer.find("> div > div > div > p")
            .html(` &copy; 2017-${(new Date()).getFullYear()} Universidad Nacional de Colombia.` +
                " - <a class=\"navbar-link\" href=\"/data_policy\">Data policy</a>");
        footer.find("> div > div > div > div > p")
            .html(
                "<a target=\"_blank\" href=\"https://github.com/JuezUN/INGInious\" class=\"navbar-link\">\n" +
                "UNCode is distributed under AGPL license" +
                "</a> - <a target=\"_blank\" href=\"https://www.inginious.org\" class=\"navbar-link\">\n" +
                "Powered by INGInious.\n</a>");
    }

    function updatePageIcon(imagePath) {
        $('link[rel="shortcut icon"]').attr('href', imagePath);
        $('link[rel="icon"]').attr('href', imagePath);
    }

    function updateTemplate() {
        // This updates all necessary changes in INGInious.
        const imagePath = window.location.origin + "/UNCode/static/images/LogotipoUNAL.png";
        updateNavbarLogo(imagePath);
        updatePageIcon(imagePath);
        updateFooter();
    }

    function addTaskContextTemplate() {
        let codeMirror = $('.CodeMirror');
        const defaultTaskContext = $("#default_task_context").text();

        if ($("#context").length !== 0 && codeMirror.length !== 0) {
            let editor = codeMirror[0].CodeMirror;
            if (editor.getDoc().getValue() === "") {
                editor.getDoc().setValue(defaultTaskContext);
            }
        }
    }

    function addTaskContextHelp() {
        let taskContext = $("#context");
        const tipsButton = "<a href='#' type='button' data-toggle='modal' data-target='#task_context_help_modal'>" +
            "<i class='fa fa-question-circle'>  Help.</a>";

        if (taskContext.length !== 0) {
            taskContext.before(tipsButton);
        }
    }

    function addTaskResultLegendButton() {
        let taskAlert = $("#task_alert");
        const legendModalButton = `<a href='#' type='button' data-toggle='modal' data-target='#task_result_legend_modal'>
            <i class='fa fa-question-circle'>  ${legend_label}</a>`;
        taskAlert.before(legendModalButton);
    }

    function updateUNCodeURL() {
        const anchors = $('a[href="http://www.inginious.org"]');
        if (anchors.length) {
            anchors.each((anchor) => anchor.href = "https://uncode.unal.edu.co");
        }
    }

    function updateCourseDocumentationLinks() {
        // This section is to update link of "How to create task?" button in course administration.
        // Now redirecting to our documentation.
        let howToCreateTaskElement = $('a[href="http://inginious.readthedocs.org/en/latest/teacher_doc/task_tuto.html"]');
        howToCreateTaskElement.attr("href", "https://github.com/JuezUN/INGInious/wiki/How-to-create-a-task");
        howToCreateTaskElement.attr("target", "_blank");

        // This section is to update link of "Documentation" button in course administration-
        // Now redirecting to our documentation.
        let documentationElement = $('a[href="http://inginious.readthedocs.org/en/latest/teacher_documentation.html"]');
        documentationElement.attr("href", "https://github.com/JuezUN/INGInious/wiki/Course-administration");
        documentationElement.attr("target", "_blank");
    }

    function stopSideBar() {
        $("#sidebar_affix").css('position', 'static');
    }

    /**
     * Hide unused grading environments when creating/editing a task. The allowed environments
     * are given in the configuration.yaml
     */
    function remove_unused_grader_environments() {
        $.ajax({
            url: '/api/getUsedGradingEnvironments/',
            type: 'get',
            contentType: 'application/json',
            dataType: 'json',
            success: function (data) {
                if (data.length !== 0) {
                    let used_grading_environments = data;
                    $('form #environment > option').each(function (_, option) {
                        let option_value = option.attributes[0].value;
                        if (used_grading_environments.indexOf(option_value) === -1) option.remove();
                    });
                }
            }
        });
    }

    /**
     * Remove unused subproblem types  when creating/editing a task. The allowed subproblems
     * are given in the configuration.yaml
     */
    function remove_unused_subproblem_types() {
        $.ajax({
            url: '/api/getUsedSubproblemTypes/',
            type: 'get',
            contentType: 'application/json',
            dataType: 'json',
            success: function (data) {
                if (data.length !== 0) {
                    let used_subproblem_types = data;
                    // Add 'subproblem_' prefix for every subproblem.
                    used_subproblem_types = used_subproblem_types.map((subproblem) => {
                        return "subproblem_" + subproblem;
                    });

                    $('#new_subproblem_type > option').each(function (_, option) {
                        let option_value = option.attributes[0].value;
                        if (used_subproblem_types.indexOf(option_value) === -1) option.remove();
                    });
                }
            }
        });
    }

    function rewrite_task_title() {
        /**
         * This function writes the name of the task instead of the id
         * on the 'edit task' section.
         */
        if (location.href.indexOf("/edit/task") > -1) {
            let title = $('#main_container #content h2')[0].innerHTML
            let firstletter = title.search("\"") + 1;
            let lastletter = title.substring(firstletter).search("\"");

            let new_title = $("#edit_task_tabs_content #name").val();
            if (new_title !== "") {
                $('#main_container #content h2')[0].innerHTML = title.substring(0, firstletter) + new_title + title.substring(firstletter + lastletter);
            }
        }
    }

    function addHomePathLTI() {
        try {
            const text = $("#lti_link");
            text.val(location.origin + text.val());
        } catch (e) {

        }
    }

    updateTemplate();
    addTaskContextTemplate();
    addTaskContextHelp();
    updateCourseDocumentationLinks();
    addTaskResultLegendButton();
    stopSideBar();
    remove_unused_subproblem_types();
    remove_unused_grader_environments();
    rewrite_task_title();
    updateUNCodeURL();
    addHomePathLTI();
});

this.studio_display_task_submit_message = (content, type, dismissible) => {
    const code = getAlertCode(content, type, dismissible);
    $('#task_edit_submit_status').html(code);

    if (dismissible) {
        window.setTimeout(function () {
            $("#task_edit_submit_status").children().fadeTo(1000, 0).slideUp(1000, function () {
                $(this).remove();
            });
        }, 10000);
    }
};
