import os.path

BASE_STATIC_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
BASE_STATIC_URL = r'/plugins/problem_bank/files/'
PLUGIN_FOLDER = os.path.dirname(os.path.realpath(__file__))
REACT_BUILD_FOLDER = os.path.join(PLUGIN_FOLDER, 'react_app', 'build')
REACT_BASE_URL = '/plugins/problem_bank/react/'
BASE_RENDERER_PATH = PLUGIN_FOLDER
