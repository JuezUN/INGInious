import json

import re
from inginious.frontend.pages.course_admin.task_edit_file import CourseTaskFiles
from .multilang_form import MultilangForm
from .hdl_form import HDLForm
from .notebook_form import NotebookForm
from .grader_form import InvalidGraderError
from .constants import get_use_minified, BASE_TEMPLATE_FOLDER


def on_task_editor_submit(course, taskid, task_data, task_fs):
    """ This method use the form from the plugin to generate
    the grader (code to use the utilities from the containers i.e multilang) and validate
    the entries in the form.

    Returns: None if successful otherwise a str
    """

    # Create form object
    task_data["generate_grader"] = "generate_grader" in task_data

    if task_data['generate_grader']:
        if task_data['environment'] == 'multiple_languages' or task_data['environment'] == 'Data Science':
            form = MultilangForm(task_data, task_fs)
        elif task_data['environment'] == 'HDL':
            form = HDLForm(task_data, task_fs)
        elif task_data['environment'] == 'Notebook':
            form = NotebookForm(task_data, task_fs)
        else:
            return

        # Try to parse and validate all the information
        try:
            form.parse()
            form.validate()
        except InvalidGraderError as error:
            return json.dumps({'status': 'error', 'message': error.message})

        # Generate the grader
        if form.task_data['generate_grader']:
            form.generate_grader()
            task_data['grader_test_cases'] = form.task_data['grader_test_cases']


def grader_generator_tab(course, taskid, task_data, template_helper):
    tab_id = 'tab_grader'
    link = '<i class="fa fa-check-circle fa-fw"></i>&nbsp; ' + _("Grader")
    task_data_list = task_data.get('grader_test_cases', [])

    check_file_existence_for_multi_lang(course, taskid, task_data_list)
    grader_test_cases_dump = json.dumps(task_data_list)
    content = template_helper.get_custom_renderer(BASE_TEMPLATE_FOLDER, layout=False).grader(task_data,
                                                                                             grader_test_cases_dump,
                                                                                             course, taskid)

    template_helper.add_javascript('https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js')
    if get_use_minified():
        template_helper.add_javascript('/grader_generator/static/js/grader_generator.min.js')
        template_helper.add_css('/grader_generator/static/css/grader_tab.min.css')
    else:
        template_helper.add_javascript('/grader_generator/static/js/grader.js')
        template_helper.add_javascript('/grader_generator/static/js/grader_generator.js')
        template_helper.add_javascript('/grader_generator/static/js/notebook_grader_generator.js')
        template_helper.add_css('/grader_generator/static/css/grader_tab.css')

    return tab_id, link, content


def check_file_existence_for_multi_lang(course, task_id, task_data):
    test_file_list = get_test_file_list_for_multi_lang(course, task_id)
    if not test_file_list:
        return

    remove_test_without_file(test_file_list, task_data)


def get_test_file_list_for_multi_lang(course, task_id):
    environment_types_to_check = ["multiple_languages", "Data Science"]
    environment = course.get_task(task_id).get_environment()
    if environment not in environment_types_to_check:
        # Only for multi lang grader format
        return

    return CourseTaskFiles.get_task_filelist(course._task_factory, course.get_id(), task_id).copy()


def remove_test_without_file(test_file_list, task_data):
    file_name_index = 2
    # To reduce the number of comparisons
    remove_public_files(test_file_list)
    test_to_remove = []
    for test in task_data:
        exist_input_file = any(file_data[file_name_index] == (test["input_file"]) for file_data in test_file_list)
        exist_output_file = any(file_data[file_name_index] == (test["output_file"]) for file_data in test_file_list)
        if not (exist_output_file and exist_input_file):
            test_to_remove.append(test)
    for test in test_to_remove:
        task_data.remove(test)


def remove_public_files(task_file_list):
    task_tests_to_remove = []
    file_full_name_index = 3
    substring = "/public/"
    for test in task_file_list:
        if test[file_full_name_index].find(substring) != -1:
            task_tests_to_remove.append(test)
    for test_to_remove in task_tests_to_remove:
        task_file_list.remove(test_to_remove)


def grader_footer(course, taskid, task_data, template_helper):
    renderer = template_helper.get_custom_renderer(BASE_TEMPLATE_FOLDER, layout=False)
    return str(renderer.grader_templates()) + str(renderer.notebook_grader_test_form_modal())


def on_file_deleted(course, task_id, path, task_factory):
    file_name = get_file_name_from_path(path)
    if file_name:
        task_data = task_factory.get_task_descriptor_content(course.get_id(), task_id)
        one_test_was_removed = remove_test_by_path_file(file_name, task_data)
        if one_test_was_removed:
            task_factory.update_task_descriptor_content(course.get_id(), task_id, task_data, "yaml")


def get_file_name_from_path(path):
    regular_exp = re.compile(r'^/[a-z0-9 _%\-]+\.[a-z0-9_]+$', flags=re.IGNORECASE)
    if regular_exp.match(path):
        return path[1:]


def remove_test_by_path_file(file_name, task_data):
    for test in task_data["grader_test_cases"]:
        test_that_uses_file = test['input_file'] == file_name or test['output_file'] == file_name
        if test_that_uses_file:
            task_data["grader_test_cases"].remove(test)
            return True
    return False
