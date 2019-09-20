from collections import OrderedDict
import copy
from datetime import datetime, timedelta

import pymongo
import web
import random

class ContestManager():

    def __init__(self, user_manager, database, course_factory, template_helper, task_factory, bank_name):
        self.user_manager = user_manager
        self.database = database
        self.course_factory = course_factory
        self.template_helper = template_helper
        self.task_factory = task_factory
        self.bank_name = bank_name

    def exists_contest(self, courseid, contestid):
        ret = False
        try:
            self.contest_is_enabled(courseid, contestid)
            ret = True
        except:
            pass
        return ret

    def get_all_techniques(self, courseid):
        #problems = [self.task_factory.get_task_descriptor_content(courseid, x).get("category","") for x in
        #            self.course_factory.get_course(courseid).get_tasks()]
        #retval = set([x for x in problems if len(x)>0])

        retval = ["Ad hoc", "Programación dinámica", "Greedy", "Dividir y conquistar", "Recursión", "Ordenamiento"]
        return retval

    def get_all_structures(self, courseid):
        #problems = [self.task_factory.get_task_descriptor_content(courseid, x).get("structure","") for x in
        #            self.course_factory.get_course(courseid).get_tasks()]
        #retval = set([x for x in problems if len(x) > 0])

        retval = ["Lista 1D", "Pila", "Cola", "Grafo", "Diccionario", "Cola de prioridad", "Árbol binario", "Lista encadenada", "Ninguna", "Lista 2D", "Conjuntos"]
        return retval

    def contest_is_enabled(self, courseid, contestid):
        course = self.course_factory.get_course(courseid)
        data = self.get_contest_data(course, contestid)
        return data["enabled"]==True

    def get_problems(self, technique, structure, difficulty, other_problems):
        problems = [(self.task_factory.get_task(self.course_factory.get_course(self.bank_name), x),
                     self.task_factory.get_task_descriptor_content(self.bank_name, x)) for x in
                    self.course_factory.get_course(self.bank_name).get_tasks()]
        difficulty = int(difficulty)
        other_problems = [x["name"] for x in other_problems]
        problems = [x for x in problems if x[0].get_id() not in other_problems]
        problems = [x for x in problems if
                    x[1].get("difficulty") == difficulty and x[1].get("structure") == structure and x[1].get(
                        "category") == technique]
        return [x[0].get_id() for x in problems]

    def get_random_problems(self, quantity, technique, structure, difficulty, other_problems):
        problems = self.get_problems(technique, structure, difficulty, other_problems)
        if len(problems) < quantity:
            raise Exception("Inconsistent information: There are not enough problems for this type: "
                            "Technique:"+technique+
                            " Difficulty:"+str(difficulty))
        retval = random.sample(problems, quantity)
        return retval

    def get_random_contest(self, random_types, other_problems):
        problems = []
        for random_type in random_types:
            quantity = int(random_type["quantity"])
            technique = random_type["technique"]
            structure = random_type["structure"]
            difficulty = int(random_type["difficulty"])
            retval = self.get_random_problems(quantity, technique, structure, difficulty, other_problems)
            problems.extend(retval)
        return problems


    def get_all_contest_data(self, course):
        contests = course.get_descriptor().get('contest', {})
        scorebs = {i: val for i, val in enumerate(contests)}
        if scorebs is None:
            scorebs = {}
        return scorebs

    def add_headers(self):
        self.template_helper.add_css(web.ctx.homepath + '/static/webapp/plugins/contests/scoreboard.css')
        self.template_helper.add_javascript(web.ctx.homepath + '/static/webapp/plugins/contests/jquery.countdown.min.js', "header")
        self.template_helper.add_javascript(web.ctx.homepath + '/static/webapp/plugins/contests/contests.js', "header")

    def delete_contest(self, course, contestid):
        course_content = self.course_factory.get_course_descriptor_content(course)
        if len(course_content["contest"])>int(contestid):
            del course_content["contest"][int(contestid)]
            self.course_factory.update_course_descriptor_content(course, course_content)
            self.database.clarifications.delete_many({"course": course, "contest": contestid})

    def get_contest_data(self, course, contestid):
        """ Returns the settings of the contest for this course """
        contests = course.get_descriptor().get('contest', {})
        scorebs = {i: val for i, val in enumerate(contests)}
        specific_contest = scorebs.get(int(contestid))
        if specific_contest is None:
            specific_contest = {}
        return specific_contest

    def get_admin_pending_clarifications(self, courseid):
        return self.database.clarifications.find(
            ({"course": courseid, "answered_by" : -1}))

    def get_admin_pending_clarifications_by_contest(self, courseid, contestid):
        return self.database.clarifications.find(
            ({"course": courseid, "answered_by" : -1, "contest": str(contestid)}))

    def get_contestant_pending_clarifications_by_contest(self, courseid, contestid):
        username = self.user_manager.session_username()
        web.debug(courseid, contestid)
        result = self.database.clarifications.find(
            ({
                "$or":  [
                            {"to": username},
                            {"to": "*"},
                            {"from": username}
                        ],
                "course": courseid,
                "answered_by" : {"$ne": -1},
                "contest": str(contestid)
            }))
        result = list([x for x in result if username not in x.get('seen_by',[])])
        web.debug(list(result))
        return result

    def get_last_contest_id(self, courseid):
        course = self.course_factory.get_course(courseid)
        contests = course.get_descriptor().get('contest', {})
        contestid = max([i for i, val in enumerate(contests)], default=0)
        return contestid

    def get_data(self, courseid, contestid, all_ranks=False, allowed_users = []):
        course = self.course_factory.get_course(courseid)
        contest_data = self.get_contest_data(course, contestid)
        if not contest_data['enabled']:
            raise web.notfound()
        start = datetime.strptime(contest_data['start'], "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(contest_data['end'], "%Y-%m-%d %H:%M:%S")
        blackout = end
        users = self.user_manager.get_course_registered_users(course, False)
        # tasks = []
        # for t in contest_data["content"]:
        # tasks.append(course.get_task(t))
        # tasks = list(course.get_tasks().keys())
        tasks = contest_data["content"]

        db_results = self.database.submissions.find(
            {'$or': [{
            "username": {"$in": users},
            "courseid": courseid,
            "submitted_on": {"$gte": start, "$lt": blackout},
            "status": "error",
            "result": {'$in': ["timeout", "overflow"]}},
            {
            "username": {"$in": users},
            "courseid": courseid,
            "submitted_on": {"$gte": start, "$lt": blackout},
            "status": "done"}]},
            {"username": True, "_id": False, "taskid": True, "result": True, "submitted_on": True, "text": True}).sort(
            [("submitted_on", pymongo.ASCENDING)])

        task_status = {taskid: {"status": "NA", "tries": 0} for taskid in tasks}
        results = {
        username: {"flag": self.user_manager.get_user_flag(username), "realname": self.user_manager.get_user_realname(username), "name": username, "tasks": copy.deepcopy(task_status)} for
        username in users}
        activity = []
        contest_name = contest_data["name"]
        conversor = {'AC': 'Accepted', 'ACF': 'Accepted', 'WA': 'Wrong Answer', 'TLE': 'Time Limit Exceed', 'RE': 'Runtime Error', 'OL': 'Output Limit'};

        # Compute stats for each submission
        task_succeeded = {taskid: False for taskid in tasks}
        for submission in db_results:
            for username in submission["username"]:
                if submission['taskid'] not in tasks:
                    continue
                if username not in users:
                    continue
                status = results[username]["tasks"][submission['taskid']]
                if status["status"] == "AC" or status["status"] == "ACF":
                    continue
                else:
                    status["time"] = submission['submitted_on']
                    if submission['result'] == "success":
                        if not task_succeeded[submission['taskid']]:
                            status["status"] = "ACF"
                            task_succeeded[submission['taskid']] = True
                        else:
                            status["status"] = "AC"
                        status["tries"] += 1
                        status["time"] = submission['submitted_on']
                        status["score"] = (submission['submitted_on']
                                           + timedelta(minutes=contest_data["penalty"] * (status["tries"] - 1))
                                           - start).total_seconds() / 60
                    elif submission['result'] == "failed" or submission['result'] == "killed":
                        if submission['text'].startswith('Runtime Error'):
                            status["status"] = "RE"
                        else:
                            status["status"] = "WA"
                        status["tries"] += 1
                    elif submission['result'] == "timeout":
                        status["status"] = "TLE"
                        status["tries"] += 1
                    elif submission['result'] == "overflow":
                        status["status"] = "OL"
                        status["tries"] += 1
                    else:  # other internal error
                        continue
                    if allowed_users!=[]:
                        if results[username]["name"] in allowed_users:
                            activity.append({"user": results[username]["name"],
                                         "when": submission['submitted_on'],
                                         "result": conversor.get(status["status"], 'Failed'),
                                         "taskid": submission['taskid']})
                    else:
                        activity.append({"user": results[username]["name"],
                                         "when": submission['submitted_on'],
                                         "result": conversor.get(status["status"], 'Failed'),
                                         "taskid": submission['taskid']})
        activity.reverse()
        # Compute current score
        for user in results:
            score = [0, 0]
            for data in list(results[user]["tasks"].values()):
                if "score" in data:
                    score[0] += 1
                    score[1] += data["score"]
            results[user]["score"] = tuple(score)

        # Sort everybody
        results = OrderedDict(sorted(list(results.items()), key=lambda t: (-t[1]["score"][0], t[1]["score"][1])))

        # Compute ranking
        old = None
        current_rank = 0
        for cid, user in enumerate(results.keys()):
            if results[user]["score"] != old:
                old = results[user]["score"]
                current_rank = cid + 1
                results[user]["rank"] = current_rank
                results[user]["displayed_rank"] = str(current_rank)
            else:
                results[user]["rank"] = current_rank
                if all_ranks:
                    results[user]["displayed_rank"] = str(current_rank)
                else:
                    results[user]["displayed_rank"] = ""

        if allowed_users!=[]:
            results = {x: results[x] for x in results.keys() if x in allowed_users}
        tasks = {x:self.task_factory.get_task_descriptor_content(courseid, x) for x in tasks}
        tasks = OrderedDict(sorted(tasks.items(), key=lambda t: t[0]))
        return course, start, end, blackout, tasks, results, activity, contestid, contest_name
