import logging

_BASE_RENDERER_PATH = 'frontend/webapp/plugins/hooks_example'
_logger = logging.getLogger("inginious.frontend.webapp.plugins.hooks_example")


def init(plugin_manager, course_factory, client, config):

    def on_task_updated(courseid, taskid, new_content):
        user_language = plugin_manager.get_user_manager().session_language()
        task_name = new_content["name"]
        descriptor = course_factory.get_course(courseid)._task_factory.get_task_descriptor_content(courseid, taskid)
        task_author = descriptor["author"]
        task_context = str(course_factory.get_course(courseid).get_task(taskid).get_context(user_language))
        tags = new_content.get("tags", [])
        course = course_factory.get_course(courseid)
        task_data = {
            "task_name": task_name,
            "task_id": taskid,
            "task_author": task_author,
            "task_context": task_context,
            "course_id": courseid,
            "course_name": course.get_name(user_language),
            "tags": [tag["name"] for _, tag in tags.items()]
        }

        data_filter = {
            "task_id": taskid,
            "course_id": courseid
        }

        plugin_manager.get_database().tasks_cache.update_one(filter=data_filter,
                                                             update={"$set": task_data}, upsert=True)

    def on_task_deleted(courseid, taskid):
        data_filter = {
            "task_id": taskid,
            "course_id": courseid
        }
        plugin_manager.get_database().tasks_cache.delete_many(data_filter)

    def on_course_deleted(courseid):
        data_filter = {
            "course_id": courseid
        }
        plugin_manager.get_database().tasks_cache.delete_many(data_filter)

    def on_course_updated(courseid, new_content):
        course_data = {
            "course_name": new_content["name"]
        }
        data_filter = {
            "course_id": courseid
        }
        plugin_manager.get_database().tasks_cache.update_many(filter=data_filter,
                                                              update={"$set": course_data})

    if "tasks_cache" not in plugin_manager.get_database().collection_names():
        plugin_manager.get_database().create_collection("tasks_cache")

    if "TextSearchIndex" not in plugin_manager.get_database().tasks_cache.index_information():
        plugin_manager.get_database().tasks_cache.create_index(
            [("course_id", "text"), ("course_name", "text"), ("task_name", "text"), ("tags", "text"),
             ("task_id", "text")], name="TextSearchIndex")

    plugin_manager.get_database().tasks_cache.create_index([("course_id", 1), ("task_id", 1)], unique=True)

    plugin_manager.add_hook('task_updated', on_task_updated)
    plugin_manager.add_hook('task_deleted', on_task_deleted)
    plugin_manager.add_hook('course_updated', on_course_updated)
    plugin_manager.add_hook('course_deleted', on_course_deleted)
