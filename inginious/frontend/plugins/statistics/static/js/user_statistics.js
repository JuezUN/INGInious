//Global namespace
const UserStatistics = {
    "colors":
        {
            "COMPILATION_ERROR": 'rgb(236,199,6)',
            "TIME_LIMIT_EXCEEDED": 'rgb(50,120,202)',
            "MEMORY_LIMIT_EXCEEDED": 'rgb(119,92,133)',
            "RUNTIME_ERROR": 'rgb(2,164,174)',
            "WRONG_ANSWER": 'rgb(227,79,54)',
            "OUTPUT_LIMIT_EXCEEDED": 'rgb(137,139,37)',
            "GRADING_RUNTIME_ERROR": 'rgb(139,62,0)',
            "ACCEPTED": 'rgb(35,181,100)'
        }
};

const UserTrialsAndBestGradeStatistic = (function () {
    function UserTrialsAndBestGradeStatistic(course_id) {
        this.course_id = course_id;
        this.div_id = "tries_per_task";
        this.RESOURCE_URL = "/api/stats/student/trials_and_best_grade";
    }

    UserTrialsAndBestGradeStatistic.prototype = Object.create(Statistic.prototype);

    UserTrialsAndBestGradeStatistic.prototype._fetchData = function () {
        return $.getJSON(this.RESOURCE_URL, {course_id: this.course_id});
    };

    UserTrialsAndBestGradeStatistic.prototype._plotData = function (tries_per_tasks) {
        const SUBMISSIONS_COUNT_TO_PIXELS = this._getRatio(tries_per_tasks);
        const plotData = {};
        const results = Object.keys(UserStatistics.colors);

        for (let index = 0; index < results.length; index++) {
            plotData[results[index]] =
                {
                    "mode": "markers",
                    "name": results[index],
                    "marker":
                        {
                            "color": UserStatistics.colors[results[index]],
                            "sizemode": "area",
                            "sizeref": SUBMISSIONS_COUNT_TO_PIXELS,
                            "size": []
                        },
                    "text": [],
                    "x": [],
                    "y": []
                }
        }

        for (let index = 0; index < tries_per_tasks.length; index++) {
            const result = tries_per_tasks[index].result;
            plotData[result]["x"].push(tries_per_tasks[index].task_name);
            plotData[result]["y"].push(tries_per_tasks[index].grade);
            plotData[result]["text"].push(tries_per_tasks[index].tried + " submissions");
            plotData[result]["marker"]["size"].push(tries_per_tasks[index].tried);
        }

        const data = [];
        for (let index = 0; index < results.length; index++) {
            data.push(plotData[results[index]]);
        }

        const layout = {
            xaxis: {title: 'Task'},
            yaxis: {title: 'Grade', range: [-10, 110]},
            margin: {t: 20},
            hovermode: 'closest',
            legend: {
                font: {
                    size: 10,
                },
                itemsizing: 'constant'
            },
        };
        Plotly.purge(this.div_id);
        Plotly.plot(this.div_id, data, layout, {showLink: false});
    };

    UserTrialsAndBestGradeStatistic.prototype._getRatio = function (tries_per_tasks) {
        let sum = 0.0;
        for (let i = 0; i < tries_per_tasks.length; i++) {
            sum += tries_per_tasks[i].tried;
        }
        const avg = sum / tries_per_tasks.length;
        return avg / 1000;
    };

    return UserTrialsAndBestGradeStatistic;
})();

const BarSubmissionsPerTasks = (function () {
    function BarSubmissionsPerTasks(course_id, id_div, include_late_submissions = false) {
        this.course_id = course_id;
        this.id_div = id_div || "submissions_per_task";
        this.RESOURCE_URL = "/api/stats/student/bar_submissions_per_tasks";
        this.normalize = false;
        this.include_late_submissions = include_late_submissions;
    }

    BarSubmissionsPerTasks.prototype = Object.create(Statistic.prototype);

    BarSubmissionsPerTasks.prototype._fetchData = function () {
        return $.getJSON(this.RESOURCE_URL, {
            course_id: this.course_id,
            late_submissions: this.include_late_submissions
        });
    };

    BarSubmissionsPerTasks.prototype.toggleNormalize = function () {
        this.normalize = !this.normalize;
        this.plotAsync();
    };

    BarSubmissionsPerTasks.prototype._plotData = function (data) {
        const data_count_obj = {};
        const tasks_id = [];

        for (let i = 0; i < data.length; ++i) {
            if (data_count_obj[data[i].task_name] == null) {
                data_count_obj[data[i].task_name] = 0;
                tasks_id.push(data[i].task_name);
            }
            data_count_obj[data[i].task_name] += data[i].count;
        }

        const colors = UserStatistics.colors;
        const compilation_error_data = this.createObjectToPlotData(data, data_count_obj, "COMPILATION_ERROR",
            colors["COMPILATION_ERROR"]);
        const time_limit_data = this.createObjectToPlotData(data, data_count_obj, "TIME_LIMIT_EXCEEDED",
            colors["TIME_LIMIT_EXCEEDED"]);
        const memory_limit_data = this.createObjectToPlotData(data, data_count_obj, "MEMORY_LIMIT_EXCEEDED",
            colors["MEMORY_LIMIT_EXCEEDED"]);
        const runtime_error_data = this.createObjectToPlotData(data, data_count_obj, "RUNTIME_ERROR",
            colors["RUNTIME_ERROR"]);
        const wrong_answer_data = this.createObjectToPlotData(data, data_count_obj, "WRONG_ANSWER",
            colors["WRONG_ANSWER"]);
        const output_limit_error_data = this.createObjectToPlotData(data, data_count_obj, "OUTPUT_LIMIT_EXCEEDED",
            colors["OUTPUT_LIMIT_EXCEEDED"]);
        const grading_error_data = this.createObjectToPlotData(data, data_count_obj, "GRADING_RUNTIME_ERROR",
            colors["GRADING_RUNTIME_ERROR"]);
        const accepted_data = this.createObjectToPlotData(data, data_count_obj, "ACCEPTED", colors["ACCEPTED"]);

        const plotData = [compilation_error_data, time_limit_data, memory_limit_data, runtime_error_data,
            wrong_answer_data, output_limit_error_data, accepted_data, grading_error_data];

        const layout = {
            barmode: 'stack',
            title: 'Submissions vs Task',
            xaxis: {
                title: 'Tasks',
                categoryorder: "array",
                categoryarray: tasks_id,
                titlefont: {
                    size: 16,
                    color: 'rgb(107, 107, 107)'
                }
            },
            yaxis: {
                title: this.normalize ? 'Percentage of submissions' : 'Number of submissions',
                titlefont: {
                    size: 16,
                    color: 'rgb(107, 107, 107)'
                }
            }
        };

        Plotly.purge(this.id_div);
        Plotly.newPlot(this.id_div, plotData, layout);
    };


    BarSubmissionsPerTasks.prototype.createObjectToPlotData = function (data, data_count_obj, verdict, color_category) {
        const plotData = {
            x: [],
            y: [],
            marker: {color: color_category},
            name: verdict,
            type: 'bar'
        };

        for (let i = 0; i < data.length; ++i) {
            if (data[i].summary_result === verdict) {
                plotData.x.push(data[i].task_name);
                if (this.normalize) {
                    plotData.y.push((data[i].count / data_count_obj[data[i].task_name]) * 100);
                } else {
                    plotData.y.push(data[i].count);
                }
            }
        }
        return plotData;
    };

    return BarSubmissionsPerTasks;
})();


$(function () {
    UserStatistics.course_id = getCourseId();
    UserStatistics.trialsAndBestGradeStatistic = new UserTrialsAndBestGradeStatistic(UserStatistics.course_id);
    UserStatistics.barSubmissionsPerTasks = new BarSubmissionsPerTasks(UserStatistics.course_id);
    UserStatistics.barLateSubmissionsPerTasks = new BarSubmissionsPerTasks(UserStatistics.course_id, "late_submissions_per_task", true);

    const tabToStatistic = {
        "trials-circle-tab": UserStatistics.trialsAndBestGradeStatistic,
        "bar-submissions-per-tasks-tab": UserStatistics.barSubmissionsPerTasks,
        "bar-late-submissions-per-tasks-tab": UserStatistics.barLateSubmissionsPerTasks
    };

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        const statistic = tabToStatistic[e.target.id];

        if (statistic) {
            statistic.plotAsync();
        }
    });
    $('.active > a[data-toggle="tab"]').trigger('shown.bs.tab');
});
