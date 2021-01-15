import os

from inginious.frontend.pages.course_admin.task_edit import CourseEditTask, CourseTaskFiles
from inginious.frontend.plugins.multilang.problems.languages import get_all_available_languages
from ..constants import use_minified

_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "templates/")


def code_preview_tab(course, taskid, task_data, template_helper):
    tab_id = "tab_code_preview"
    link = "<i class='fa fa-check-circle fa-fw'></i>&nbsp; " + _("Code template")
    code_preview_pairs = task_data.get("code_preview_pairs", {})
    if code_preview_pairs is None:
        code_preview_pairs = {}
    content = template_helper.get_custom_renderer(
        _TEMPLATES_PATH, layout=False).code_preview(course.get_id(), taskid, code_preview_pairs,
                                                    get_all_available_languages())

    if use_minified():
        template_helper.add_javascript("/code_preview/static/js/code_preview_load.min.js")
    else:
        template_helper.add_javascript("/code_preview/static/js/code_preview_load.js")

    return tab_id, link, content


def on_task_editor_submit(course, taskid, task_data, task_fs):
    task_data["code_preview_pairs"] = CourseEditTask.dict_from_prefix("code_preview_pairs", task_data)

    available_languages = get_all_available_languages()
    task_files = CourseTaskFiles.get_task_filelist(course._task_factory, course.get_id(), taskid)
    task_files = {complete_name[1:] if complete_name.startswith("/") else complete_name for
                  level, is_directory, name, complete_name in task_files}

    if "code_preview_pairs" in task_data and task_data["code_preview_pairs"]:
        for language, file in task_data["code_preview_pairs"].items():
            if language not in available_languages:
                del task_data["code_preview_pairs"][language]
            if file not in task_files:
                del task_data["code_preview_pairs"][language]

    to_delete = []
    for key in task_data:
        if "code_preview_pairs[" in key:
            to_delete.append(key)

    for key in to_delete:
        del task_data[key]
