#!/bin/python3
import yaml
import sys
import os

with open(os.path.join(sys.argv[1] , "submission.test"), "r") as stream:
    try:
        info = yaml.safe_load(stream)['input']
        problem_id = filter(lambda x: '/' not in x, info.keys())
        problem_id = filter(lambda x: '@' not in x, problem_id)
        # Just the beginning element
        problem_id = list(problem_id)[0]

        code = info[problem_id]

        # Write the this code into a new file with the type
        code_language = info[problem_id + '/language']
        if code_language in ['cpp11', 'cpp']:
            with open(os.path.join(sys.argv[1], 'code.cpp'), 'w') as file:
                file.write(code)
        elif code_language in ['python3']:
            with open(os.path.join(sys.argv[1], 'code.py'), 'w') as file:
                file.write(code)
    except yaml.YAMLError as exc:
        print(exc)
