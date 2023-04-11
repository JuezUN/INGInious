def project_detail_user_tasks(user_tasks):
    return [{
        "grade": s["grade"],
        "username": s["username"],
        "submission": project_submission(s.get("submission", None))
    } for s in user_tasks]


def task_submissions_detail(submissions, summary_result):
    return [{
        "grade": submission["grade"],
        "username": submission["username"],
        "id": str(submission["_id"]),
        "status": submission["status"],
        "submitted_on": str(submission["submitted_on"]),
        "summary_result": summary_result

    } for submission in submissions if submission.get("custom", {}).get("custom_summary_result", "ACCEPTED" if submission["result"] == "success" else "WRONG_ANSWER") == summary_result]


def project_submission(submission):
    if submission is None:
        return None

    return {
        "id": str(submission["_id"]),
        "submitted_on": submission["submitted_on"].isoformat(),
        "taskId": submission["taskid"],
        "status": submission["status"],
        "result": submission["result"],
        "grade": submission["grade"],
        "summary_result": submission.get("custom", {}).get("custom_summary_result", "ACCEPTED" if submission["result"] == "success" else "WRONG_ANSWER")
    }

def project_detail_best_user_tasks(user_tasks, summary_result):
    return [{
        "grade": s["grade"],
        "username": s["username"],
        "submission": project_best_submission(s.get("submission", None), summary_result)
    } for s in user_tasks if s.get("submission", None).get("custom", {}).get("custom_summary_result", "ACCEPTED" if s.get("submission", None).get("result",{}) == "success" else "WRONG_ANSWER") == summary_result]

def project_best_submission(submission, summary_result):
    if submission is None:
        return None
   
    return {
        "id": str(submission["_id"]),
        "submitted_on": submission["submitted_on"].isoformat(),
        "taskId": submission["taskid"],
        "status": submission["status"],
        "result": submission["result"],
        "grade": submission["grade"],
        "summary_result": summary_result
    }