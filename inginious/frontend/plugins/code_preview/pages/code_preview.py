import os

_BASE_RENDERER_PATH = os.path.dirname(__file__)

def code_preview_tab(course, taskid, task_data, template_helper):
    tab_id = 'tab_preview'
    link = '<i class="fa fa-check-circle fa-fw"></i>&nbsp; Preview'
    content = template_helper.get_custom_renderer(_BASE_RENDERER_PATH, layout=False).code_preview(taskid)
    
    return tab_id, link, content