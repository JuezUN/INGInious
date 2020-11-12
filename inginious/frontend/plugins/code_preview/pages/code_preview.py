import os
import json

from inginious.frontend.pages.course_admin.task_edit import CourseEditTask

_BASE_RENDERER_PATH = os.path.dirname(__file__)


def code_preview_tab(course, taskid, task_data, template_helper):
    tab_id = 'tab_preview'
    link = '<i class="fa fa-check-circle fa-fw"></i>&nbsp; ' + _('Preview')
    code_preview_pairs = json.dumps(task_data.get('code_preview_pairs', []))
    content = template_helper.get_custom_renderer(_BASE_RENDERER_PATH, layout=False).code_preview(taskid,
                                                                                                  code_preview_pairs)
    return tab_id, link, content


def on_task_editor_submit(course, taskid, task_data, task_fs):
    task_data['code_preview_pairs'] = CourseEditTask.dict_from_prefix('code_preview_pairs', task_data)

    to_delete = []
    for key in task_data:
        if 'code_preview_pairs[' in key:
            to_delete.append(key)

    for key in to_delete:
        del task_data[key]
