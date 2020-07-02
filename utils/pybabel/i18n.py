"""
File intended to manage automatically the i18n folder
"""
import argparse
import os
import subprocess

global _frontend_path
global _i18n_path
global _pybabel_conf_path


def get_languages():
    completed_process = subprocess.run(['ls', _i18n_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return completed_process.stdout.decode('utf-8').split()


def extract_messages():
    subprocess.run(['pybabel', 'extract', '-F', _pybabel_conf_path, './', '-o', '/tmp/messages.pot'])


def update_messages():
    for language in languages:
        messages_path = os.path.join(_i18n_path, language, 'LC_MESSAGES/messages.po')
        subprocess.run(['pybabel', 'update', '-i', '/tmp/messages.pot', '-o', messages_path, '-l', language])


def compile_messages():
    for language in languages:
        messages_path = os.path.join(_i18n_path, language, 'LC_MESSAGES/messages.po')
        compile_path = os.path.join(_i18n_path, language, 'LC_MESSAGES/messages.mo')
        subprocess.run(['pybabel', 'compile', '-i', messages_path, '-o', compile_path, '-l', language])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process automatically i18n folders.')
    parser.add_argument('--actions', metavar='-a', choices=['extract', 'update', 'compile', 'all'], nargs='+',
                        help='Actions to apply using pybabel')

    parser.add_argument('--path', metavar='-f', type=str, help='UNCode repository path')
    args = parser.parse_args()

    _frontend_path = os.path.join(args.path, 'inginious/frontend')
    _i18n_path = os.path.join(_frontend_path, 'i18n')
    _pybabel_conf_path = os.path.join(_frontend_path, 'babel.cfg')

    actions = args.actions
    languages = get_languages()
    if 'extract' in actions:
        extract_messages()
    if 'update' in actions:
        update_messages()
    if 'compile' in actions:
        compile_messages()
    if 'all' in actions:
        extract_messages()
        update_messages()
        compile_messages()
