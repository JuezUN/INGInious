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

    check_file_existence(course, taskid, task_data_list)
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


def check_file_existence(course, task_id, task_data):
    task_list = CourseTaskFiles.get_task_filelist(course._task_factory, course.get_id(), task_id)
    file_name_index = 2
    for task in task_data:
        exist_input_file = any(file_name[file_name_index] == task["input_file"] for file_name in task_list)
        exist_output_file = any(file_name[file_name_index] == task["output_file"] for file_name in task_list)
        if not (exist_output_file and exist_input_file):
            task_data.remove(task)
    print(task_data)


def grader_footer(course, taskid, task_data, template_helper):
    renderer = template_helper.get_custom_renderer(BASE_TEMPLATE_FOLDER, layout=False)
    return str(renderer.grader_templates()) + str(renderer.notebook_grader_test_form_modal())
