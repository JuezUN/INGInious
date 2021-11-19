import json

import re
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

    problem_id = list(task_data['problems'])[0]
    problem_type = task_data['problems'][problem_id]["type"]

    grader_environment = task_data['environment']
    if problem_type in ['code_multiple_languages', 'code_file_multiple_languages']:
        if grader_environment not in ['multiple_languages', 'HDL', 'Data Science']:
            return json.dumps({"status":"error","message": "Cannot set a 'Code Multiple Languages' or 'Code File Multiple Languages' problem with a 'Notebook' grading environment"})
    elif problem_type == 'notebook_file':
        if grader_environment != 'Notebook':
            return json.dumps({"status":"error","message": "Cannot set a 'Notebook' problem in a non 'Notebook' grading environment"})


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
    grader_test_cases_dump = json.dumps(task_data.get('grader_test_cases', []))
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


def grader_footer(course, taskid, task_data, template_helper):
    renderer = template_helper.get_custom_renderer(BASE_TEMPLATE_FOLDER, layout=False)
    return str(renderer.grader_templates()) + str(renderer.notebook_grader_test_form_modal())


def on_file_deleted(course, task_id, path, task_factory):
    """ It's called when a file of a task is deleted.
    This function removes The test related with the file that was deleted if the file was a root file
    in a multi lang environment
     """
    if not _is_multi_lang(course, task_id):
        return
    file_name = get_file_name_from_path(path)
    if file_name:
        task_data = task_factory.get_task_descriptor_content(course.get_id(), task_id)
        one_test_was_removed = remove_test_by_file_name(file_name, task_data)
        if one_test_was_removed:
            task_factory.update_task_descriptor_content(course.get_id(), task_id, task_data, "yaml")


def _is_multi_lang(course, task_id):
    """ Indicates whether the task uses multi lang environment """
    environment_types_to_check = {"multiple_languages", "Data Science"}
    environment = course.get_task(task_id).get_environment()
    return environment in environment_types_to_check


def get_file_name_from_path(path):
    """ returns the name of the file inside path if is a root file
    * root file -> /text.text
    * public file -> /public/text.text
    """
    regular_exp = re.compile(r'^/[^.\n/]+\.[a-z0-9_]+$', flags=re.IGNORECASE)
    if regular_exp.match(path):
        return path[1:]


def remove_test_by_file_name(file_name, task_data):
    """ Search a test by a file name and remove it """
    for test in task_data["grader_test_cases"]:
        test_that_uses_file = test['input_file'] == file_name or test['output_file'] == file_name
        if test_that_uses_file:
            task_data["grader_test_cases"].remove(test)
            return True
    return False
