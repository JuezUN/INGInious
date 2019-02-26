from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from collections import OrderedDict
import web
import os
import posixpath
import urllib
# import numpy as np
from bson.objectid import ObjectId
from inginious.frontend.pages.utils import INGIniousAuthPage, INGIniousPage
from inginious.common.filesystems.local import LocalFSProvider
# import scipy as sp
import sklearn.cluster as sklCluster
import sklearn.manifold as sklManifold
import numpy as np
import json



_BASE_RENDERER_PATH = 'frontend/plugins/space_visualization'
_BASE_STATIC_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')


class StaticResourcePage(INGIniousPage):
    def GET(self, path):
        path_norm = posixpath.normpath(urllib.parse.unquote(path))

        static_folder = LocalFSProvider(_BASE_STATIC_FOLDER)
        (method, mimetype_or_none, file_or_url) = static_folder.distribute(path_norm, False)

        if method == "local":
            web.header('Content-Type', mimetype_or_none)
            return file_or_url
        elif method == "url":
            raise web.redirect(file_or_url)

        raise web.notfound()


def space_visualization_course_admin_menu_hook(course):
    return "space_visualization", '<i class="fa fa-bar-chart" aria-hidden="true"></i> Space Visualization'

#listado de task
class VisualizationCourseTaskListPage(INGIniousAdminPage):
    """ List informations about all tasks """

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, _ = self.get_course_and_check_rights(courseid)
        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, _ = self.get_course_and_check_rights(courseid)
        data = web.input(task=[])

        if "task" in data:
            # Change tasks order
            for index, taskid in enumerate(data["task"]):
                try:
                    task = self.task_factory.get_task_descriptor_content(courseid, taskid)
                    task["order"] = index
                    self.task_factory.update_task_descriptor_content(courseid, taskid, task)
                except:
                    pass

        return self.page(course)

    def submission_url_generator(self, taskid):
        """ Generates a submission url """
        return "?format=taskid%2Fusername&tasks=" + taskid

    def page(self, course):
        """ Get all data and display the page """
        url = 'space_visualization'
        url = 'space_visualization'
        data = list(self.database.user_tasks.aggregate(
            [
                {
                    "$match":
                        {
                            "courseid": course.get_id(),
                            "username": {"$in": self.user_manager.get_course_registered_users(course, False)}
                        }
                },
                {
                    "$group":
                        {
                            "_id": "$taskid",
                            "viewed": {"$sum": 1},
                            "attempted": {"$sum": {"$cond": [{"$ne": ["$tried", 0]}, 1, 0]}},
                            "attempts": {"$sum": "$tried"},
                            "succeeded": {"$sum": {"$cond": ["$succeeded", 1, 0]}}
                        }
                }
            ]))

        # Load tasks and verify exceptions
        files = self.task_factory.get_readable_tasks(course)
        output = {}
        errors = []
        for task in files:
            try:
                output[task] = course.get_task(task)
            except Exception as inst:
                errors.append({"taskid": task, "error": str(inst)})
        tasks = OrderedDict(sorted(list(output.items()), key=lambda t: (t[1].get_order(), t[1].get_id())))

        # Now load additional informations
        result = OrderedDict()
        for taskid in tasks:
            result[taskid] = {"name": tasks[taskid].get_name(self.user_manager.session_language()), "viewed": 0, "attempted": 0, "attempts": 0, "succeeded": 0,
                              "url": self.submission_url_generator(taskid)}

        for entry in data:
            if entry["_id"] in result:
                result[entry["_id"]]["viewed"] = entry["viewed"]
                result[entry["_id"]]["attempted"] = entry["attempted"]
                result[entry["_id"]]["attempts"] = entry["attempts"]
                result[entry["_id"]]["succeeded"] = entry["succeeded"]

        return self.template_helper.get_custom_renderer(_BASE_RENDERER_PATH).task_list(course, result, errors, url)

class SpaceVisualizationPage(INGIniousAdminPage):


    def communicate_jar(self,path_jar, path_code, lang, distance):
        cm = 'java -jar {PATH_JAR} {PATH_CODE} {LANG} {DISTANCE}'.format(PATH_JAR=path_jar, PATH_CODE=path_code,
                                                                         LANG=lang, DISTANCE=distance)
        print(cm)
        os.system(cm)

    def do_visualization(self):
        distances = np.loadtxt("distances.txt")  # [:50,:50]
        gamma = 0.1

        similitudes = np.exp((-gamma * distances ** 2) / distances.std())



        clusters = sklCluster.AffinityPropagation(affinity='precomputed', max_iter=100, verbose=True).fit(
            similitudes).labels_
        se = sklManifold.MDS(2, dissimilarity='precomputed', random_state=0).fit_transform(distances)


        nodes = {}
        for k in range(0, len(similitudes)):
            nodes[k] = {"userID": k, "in": 0, "out": 0, "label": str(clusters[k])}

        edges = {}
        treshold = 0.95
        n_tam = len(similitudes[0])
        for k in range(len(similitudes[0])):
            for j in range(len(similitudes[0])):
                if similitudes[k][j] >= treshold and k != j:
                    edges[k * n_tam + j] = {"source": k, "target": j}
        print("here")

        return nodes, edges

    def get_submission(self, submissionid):
        """ Get a submission from the database """
        sub = self.database.submissions.find_one({'_id': ObjectId(submissionid)})

        return sub

    def POST_AUTH(self, course_id, task_id):
        """ POST request """
        course, task = self.get_course_and_check_rights(course_id, task_id)
        data = web.input()




        print("here")
        if "type" in data.keys() and data.type == "distance":
            # path_jar = '/media/windows/Visual/APDCmd.jar'
            # Funcion en la cual se descargan los codigos.
            dataSubmission = list(self.database.submissions.aggregate(

                [
                    {
                        "$match":
                            {
                                "courseid": course_id,
                                "taskid": task_id,
                                "username": {"$in": self.user_manager.get_course_registered_users(course, False)},

                            }
                    },
                    {
                        "$project": {

                            "taskid": 1,
                            "result": 1,
                            "submitted_on": 1,
                            "username": 1,
                            "custom": 1

                        }
                    }

                ]))

            path_jar = '/home/uncode/Visual/APDCmd.jar'
            path_code = '/home/uncode/Visual/sourceCodes'

            # Eliminando todos lo archivos en el folder de codigos.
            for the_file in os.listdir(path_code):
                file_path = os.path.join(path_code, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

            idx = 0
            for entry in dataSubmission:
                print(entry["_id"])
                submission = self.submission_manager.get_submission(entry["_id"], user_check=False)
                submission_input = self.submission_manager.get_input_from_submission(submission)

                # print("Aca mostrando cosas")
                #print(submission_input)
                # print(submission_input['input'])
                # print(submission_input['input']['sum'])
                print(submission_input['input']['sum/language'])
                data_input = submission_input

                if (submission_input['input']['sum/language'].startswith("java")):
                    fileName = '/{COURSE}.{SOURCE_CODE}.{USER}.{TASK_NAME}.java'.format(
                        COURSE=data_input['courseid'], SOURCE_CODE=str(entry["_id"]), USER=data_input['username'][0], TASK_NAME=data_input['taskid']
                    )
                    #path_code + "/code" + str(entry["_id"]) + ".java"
                    #print(path_code + fileName)
                    f = open(path_code +fileName, "w")
                    f.write(submission_input['input']['sum'])

                    f.close()


            lang = 'java'
            distance = data["distance"]
            print (distance)

            self.communicate_jar(path_jar, path_code, lang, distance)

            return self.page(course, task)

        if "type" in data.keys() and data.type == "visualization":
            type_vis = data["visualization"]

            nodes, edges = self.do_visualization()
            #print(nodes)
            #print(edges)
            temp = {"nodes": nodes, "edges": edges}


            json_file = json.dumps(temp)


            return json_file

        else:

            # TODO: verificar que exista exactamente un elemento. TOMAR MEDIDAS PREVENTIVAS EN CASO CONTRARIO
            problem_id = task.get_problems()[0].get_id()

            print("TASK", problem_id)
            sc_id = data['source_code_id']
            submission = self.get_submission(sc_id)
            input = self.submission_manager.get_input_from_submission(submission)
            submission_input = input['input'][problem_id]
            print (input)
            language = input['input'][problem_id + "/language"]
            print(submission_input)

            return self.page(course, task, submission_input, language)


    def GET_AUTH(self, course_id, task_id):
        # print("-->", course_id, task_id, submission_id)
        course, task = self.get_course_and_check_rights(course_id, task_id)

        self.template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-1.30.0.min.js")
        self.template_helper.add_javascript("https://cdn.jsdelivr.net/npm/lodash@4.17.4/lodash.min.js")
        self.template_helper.add_javascript("https://d3js.org/d3.v5.min.js")
        # self.template_helper.add_css("/space_visualization/static/css/space_visualization.css")
        # self.template_helper.add_javascript("/space_visualization/static/js/d3.v3.min.js")
        # self.template_helper.add_css("/space_visualization/static/css/svg.css")


        return self.page(course, task)

    def page(self, course, task, submission_input="", language="python"):

        url = 'space_visualization'

        #trace =
        return (
            self.template_helper.get_custom_renderer(_BASE_RENDERER_PATH).space_visualization(course, task, submission_input, url, language)
        )