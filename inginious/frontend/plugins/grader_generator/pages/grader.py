import json
import os
from .multilang_form import MultilangForm
from .hdl_form import HDLForm
from .grader_form import InvalidGraderError

from .constants import get_use_minified

_BASE_RENDERER_PATH = os.path.dirname(__file__)

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
    link = '<i class="fa fa-check-circle fa-fw"></i>&nbsp; Grader'
    grader_test_cases_dump = json.dumps(task_data.get('grader_test_cases', []))
    content = template_helper.get_custom_renderer(_BASE_RENDERER_PATH, layout=False).grader(task_data,
                                                                                            grader_test_cases_dump,
                                                                                            course, taskid)
    if get_use_minified():
        template_helper.add_javascript('/grader_generator/static/js/grader_generator.min.js')
    else:
        template_helper.add_javascript('/grader_generator/static/js/grader_generator.js')


    return tab_id, link, content


def grader_footer(course, taskid, task_data, template_helper):
    return template_helper.get_custom_renderer(_BASE_RENDERER_PATH, layout=False).grader_templates()