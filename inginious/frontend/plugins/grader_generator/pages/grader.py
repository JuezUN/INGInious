import json

from inginious.common.task_factory import TaskFactory
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
    environment_types_to_check = ["multiple_languages", "Data Science"]
    environment = course.get_task(task_id).get_environment()
    if environment not in environment_types_to_check:
        # It only check for multi lang grader format
        return

    test_file_list = CourseTaskFiles.get_task_filelist(course._task_factory, course.get_id(), task_id).copy()

    remove_test_without_file(test_file_list, task_data)


def remove_test_without_file(test_file_list, task_data):
    file_name_index = 2
    # To reduce the number of comparisons
    remove_public_files(test_file_list)
    task_to_remove = []
    for task in task_data:
        exist_input_file = any(file_data[file_name_index] == (task["input_file"]) for file_data in test_file_list)
        exist_output_file = any(file_data[file_name_index] == (task["output_file"]) for file_data in test_file_list)
        if not (exist_output_file and exist_input_file):
            task_to_remove.append(task)
    for task in task_to_remove:
        task_data.remove(task)


def remove_public_files(task_file_list):
    task_path_to_remove = []
    file_full_name_index = 3
    substring = "/public/"
    for path in task_file_list:
        if path[file_full_name_index].find(substring) != -1:
            task_path_to_remove.append(path)
    for path_to_remove in task_path_to_remove:
        task_file_list.remove(path_to_remove)


def grader_footer(course, taskid, task_data, template_helper):
    renderer = template_helper.get_custom_renderer(BASE_TEMPLATE_FOLDER, layout=False)
    return str(renderer.grader_templates()) + str(renderer.notebook_grader_test_form_modal())
