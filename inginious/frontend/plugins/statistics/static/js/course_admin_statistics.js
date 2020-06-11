const COLOR_COMPILATION_ERROR = 'rgb(236,199,6)';
const COLOR_TIME_LIMIT_EXCEEDED = 'rgb(50,120,202)';
const COLOR_MEMORY_LIMIT_EXCEEDED = 'rgb(119,92,133)';
const COLOR_RUNTIME_ERROR = 'rgb(2,164,174)';
const COLOR_WRONG_ANSWER = 'rgb(227,79,54)';
const COLOR_OUTPUT_LIMIT_EXCEEDED = 'rgb(137,139,37)';
const COLOR_GRADING_RUNTIME_ERROR = 'rgb(139,62,0)';
const COLOR_INTERNAL_ERROR = 'rgb(139,0,58)';
const COLOR_ACCEPTED = 'rgb(35,181,100)';
const COLOR_LABEL = 'rgb(107, 107, 107)';

const errorContainer = $("#plotErrorContainer");

function getDataNormalized(data_entry, data_count_obj) {
    return data_entry.count / data_count_obj[data_entry.task_id] * 100;
}

function getData(data_entry, _) {
    return data_entry.count;
}

function createObjectToPlotData(data, data_count_obj, tasks_ids, verdict, color_category, get_function) {
    const plotData = {
        x: [],
        y: [],
        marker: {color: color_category},
        name: verdict,
        type: 'bar'
    };

    for (let i = 0; i < data.length; ++i) {
        if (data[i].summary_result === verdict) {
            plotData.x.push(tasks_ids[data[i].task_id]);
            plotData.y.push(get_function(data[i], data_count_obj));
        }
    }
    return plotData;
}

function plotVerdictStatisticsChart(id_div, data, statistic_title, normalized, api_url, generateTable) {
    const data_count_obj = {};
    const tasks_ids = {};
    const tasks_names = {};
    const yLabel = normalized ? "Percentage of submissions" : "Number of submissions";

    let tick = 0;
    for (let i = 0; i < data.length; i++) {
        if (data_count_obj[data[i].task_id] == null) {
            data_count_obj[data[i].task_id] = 0;
            tasks_names[tick] = data[i].task_name;
            tasks_ids[data[i].task_id] = tick++;
        }
        data_count_obj[data[i].task_id] += data[i].count;
    }

    const get_function = normalized ? getDataNormalized : getData;

    const compilation_error_data = createObjectToPlotData(data, data_count_obj, tasks_ids, "COMPILATION_ERROR",
        COLOR_COMPILATION_ERROR, get_function);
    const time_limit_data = createObjectToPlotData(data, data_count_obj, tasks_ids, "TIME_LIMIT_EXCEEDED",
        COLOR_TIME_LIMIT_EXCEEDED, get_function);
    const memory_limit_data = createObjectToPlotData(data, data_count_obj, tasks_ids, "MEMORY_LIMIT_EXCEEDED",
        COLOR_MEMORY_LIMIT_EXCEEDED, get_function);
    const runtime_error_data = createObjectToPlotData(data, data_count_obj, tasks_ids, "RUNTIME_ERROR",
        COLOR_RUNTIME_ERROR, get_function);
    const wrong_answer_data = createObjectToPlotData(data, data_count_obj, tasks_ids, "WRONG_ANSWER",
        COLOR_WRONG_ANSWER, get_function);
    const internal_error_data = createObjectToPlotData(data, data_count_obj, tasks_ids, "INTERNAL_ERROR",
        COLOR_INTERNAL_ERROR, get_function);
    const output_limit_error_data = createObjectToPlotData(data, data_count_obj, tasks_ids, "OUTPUT_LIMIT_EXCEEDED",
        COLOR_OUTPUT_LIMIT_EXCEEDED, get_function);
    const grading_error_data = createObjectToPlotData(data, data_count_obj, tasks_ids, "GRADING_RUNTIME_ERROR",
        COLOR_GRADING_RUNTIME_ERROR, get_function);
    const accepted_data = createObjectToPlotData(data, data_count_obj, tasks_ids, "ACCEPTED",
        COLOR_ACCEPTED, get_function);

    const plotData = [compilation_error_data, time_limit_data, memory_limit_data, runtime_error_data, wrong_answer_data,
        output_limit_error_data, accepted_data, grading_error_data, internal_error_data];

    const layout = {
        barmode: 'stack',
        title: statistic_title,
        hovermode: 'closest',
        xaxis: {
            title: 'Tasks',
            tickmode: "array",
            tickvals: Object.values(tasks_ids),
            ticktext: Object.values(tasks_names),
            titlefont: {
                size: 16,
                color: COLOR_LABEL
            }
        },
        yaxis: {
            title: yLabel,
            titlefont: {
                size: 16,
                color: COLOR_LABEL
            }
        }
    };

    Plotly.purge(id_div);
    Plotly.newPlot(id_div, plotData, layout);

    const container = $("#" + id_div);
    container.unbind('plotly_click');
    container[0].on('plotly_click', function (data) {
        const point = data.points[0];
        const pointNumber = point.pointNumber;
        const taskId = Object.keys(tasks_ids)[point.data.x[pointNumber]];
        const summaryResult = point.data.name;
        $.get(api_url, {
            course_id: adminStatistics.courseId,
            task_id: taskId,
            summary_result: summaryResult
        }, generateTable, "json").fail(function () {
            errorContainer.html(createAlertHtml("alert-danger",
                "Something went wrong while fetching the submission list. Try again later."));
        });
    });
}

const GradeDistributionStatistic = (function () {
    function GradeDistributionStatistic(containerId) {
        Statistic.call(this);
        this.containerId = containerId;
    }

    GradeDistributionStatistic.prototype = Object.create(Statistic.prototype);

    GradeDistributionStatistic.prototype._plotData = function (data) {
        const plotData = _.map(data, function (item) {
            return {
                y: item.grades,
                taskId: item.task_id,
                name: item.task_name,
                boxmean: true,
                type: 'box',
                marker: {
                    outliercolor: 'rgba(219, 64, 82, 0.6)',
                    line: {
                        outliercolor: 'rgba(219, 64, 82, 1.0)',
                        outlierwidth: 2
                    }
                },
                boxpoints: 'all'
            };
        });

        const layout = {
            xaxis: {title: 'Task name', type: 'category'},
            yaxis: {title: 'Grade', type: 'linear', range: [-10, 110], zeroline: false}
        };

        Plotly.newPlot(this.containerId, plotData, layout);

        const container = $("#" + this.containerId);
        container.unbind('plotly_click');
        container[0].on('plotly_click', function (data) {
            const point = data.points[0];
            const taskId = point.data.taskId;

            errorContainer.empty();

            $.get('/api/stats/admin/grade_distribution_details', {
                course_id: adminStatistics.courseId,
                task_id: taskId
            }, function (result) {
                generateSubmissionTable("statisticsGradeDistributionTable", result);
            }, "json").fail(function () {
                errorContainer.html(createAlertHtml("alert-danger", "Something went wrong while fetching the " +
                    "submission list. Try again later."));
            });
        });
    };

    GradeDistributionStatistic.prototype._fetchData = function () {
        return $.get('/api/stats/admin/grade_distribution', {course_id: adminStatistics.courseId}, null, "json");
    };

    return GradeDistributionStatistic;
})();

GradeDistributionStatistic.prototype._fetchData = function () {
    return $.get('/api/stats/admin/grade_distribution', {course_id: adminStatistics.courseId}, null, "json");
};

GradeDistributionStatistic.prototype._fetchCsvData = function () {
    return this._fetchAndCacheData().then(function (data) {
        // Unwrap each grade so the CSV is properly generated.
        return _.flatMap(data, function (taskElement) {
            return _.map(taskElement.grades, function (grade) {
                return {
                    task_id: taskElement.task_id,
                    task_name: taskElement.task_name,
                    grade: grade
                };
            });
        });
    });
};

const SubmissionsVerdictStatistic = (function () {
    function SubmissionsVerdictStatistic(containerId) {
        Statistic.call(this);
        this.toggle_normalize_submissions_per_tasks = false;
        this.containerId = containerId;
    }

    SubmissionsVerdictStatistic.prototype = Object.create(Statistic.prototype);

    SubmissionsVerdictStatistic.prototype._plotData = function (data) {
        const title = "Submissions Vs Verdicts (ALL)";
        const api_url = "/api/stats/admin/submissions_verdict_details";
        const tableGenerator = generateVerdictSubmissionTable;
        const table_id = "submissionsVerdictTable";

        plotVerdictStatisticsChart(this.containerId, data, title,
            this.toggle_normalize_submissions_per_tasks, api_url, function (result) {
                tableGenerator(table_id, result);
            });
    };

    SubmissionsVerdictStatistic.prototype._fetchData = function () {
        return $.get('/api/stats/admin/submissions_verdict', {course_id: adminStatistics.courseId}, null, "json");
    };

    SubmissionsVerdictStatistic.prototype.toggleNormalize = function () {
        this.toggle_normalize_submissions_per_tasks = !this.toggle_normalize_submissions_per_tasks;
        this.plotAsync();
    };

    return SubmissionsVerdictStatistic;
})();

const BestSubmissionsVerdictStatistic = (function () {
    function BestSubmissionsVerdictStatistic(containerId) {
        Statistic.call(this);
        this.toggle_normalize_best_submissions_per_tasks = false;
        this.containerId = containerId;
    }

    BestSubmissionsVerdictStatistic.prototype = Object.create(Statistic.prototype);

    BestSubmissionsVerdictStatistic.prototype._plotData = function (data) {
        const title = "Submissions Vs Verdicts (BEST)";
        const api_url = "/api/stats/admin/best_submissions_verdict_details";
        const tableGenerator = generateSubmissionTable;
        const table_id = "bestSubmissionsVerdictTable";

        plotVerdictStatisticsChart(this.containerId, data, title,
            this.toggle_normalize_best_submissions_per_tasks, api_url, function (result) {
                tableGenerator(table_id, result);
            });
    };

    BestSubmissionsVerdictStatistic.prototype._fetchData = function () {
        return $.get('/api/stats/admin/best_submissions_verdict', {course_id: adminStatistics.courseId}, null, "json");
    };

    BestSubmissionsVerdictStatistic.prototype.toggleNormalize = function () {
        this.toggle_normalize_best_submissions_per_tasks = !this.toggle_normalize_best_submissions_per_tasks;
        this.plotAsync();
    };

    return BestSubmissionsVerdictStatistic;
})();

const GradeCountStatistic = (function () {
    function GradeCountStatistic(containerId) {
        Statistic.call(this);
        this.containerId = containerId;
    }

    GradeCountStatistic.prototype = Object.create(Statistic.prototype);

    GradeCountStatistic.prototype._plotData = function (data) {
        const allGrades = _.flatMap(data, function (item) {
            return item.grades;
        });

        const studentCountToPixels = 1e-03 * _.meanBy(allGrades, function (item) {
            return item.count;
        });

        const plotData = {
            mode: 'markers',
            x: [],
            y: [],
            taskIds: [],
            text: [],
            marker: {
                sizemode: "area",
                size: [],
                sizeref: studentCountToPixels
            }
        };

        for (let i = 0; i < data.length; ++i) {
            const grades = data[i].grades;
            for (let j = 0; j < grades.length; ++j) {
                plotData.x.push(data[i].task_name);
                plotData.y.push(grades[j].grade);
                plotData.taskIds.push(data[i].task_id);
                plotData.text.push("Students: " + grades[j].count);
                plotData.marker.size.push(grades[j].count);
            }
        }

        const layout = {
            xaxis: {title: 'Task name', type: 'category'},
            yaxis: {title: 'Grade', type: 'linear', range: [-10, 110]},
            hovermode: 'closest'
        };

        Plotly.newPlot(this.containerId, [plotData], layout);

        const container = $("#" + this.containerId);
        container.unbind('plotly_click');
        container[0].on('plotly_click', function (data) {
            const point = data.points[0];
            const pointNumber = point.pointNumber;
            const taskId = point.data.taskIds[pointNumber];
            const grade = point.y;

            errorContainer.empty();

            $.get('/api/stats/admin/grade_count_details', {
                course_id: adminStatistics.courseId,
                task_id: taskId,
                grade: grade
            }, function (result) {
                generateSubmissionTable("statisticsGradeTable", result);
            }, "json").fail(function () {
                errorContainer.html(createAlertHtml("alert-danger", "Something went wrong while fetching the " +
                    "submission list. Try again later."));
            });
        });
    };

    GradeCountStatistic.prototype._fetchData = function () {
        return $.get('/api/stats/admin/grade_count', {course_id: adminStatistics.courseId}, null, "json");
    };

    GradeCountStatistic.prototype._fetchCsvData = function () {
        return this._fetchAndCacheData().then(function (data) {
            // Unwrap each grade so the CSV is properly generated.
            return _.flatMap(data, function (taskElement) {
                return _.map(taskElement.grades, function (gradeElement) {
                    return {
                        task_id: taskElement.task_id,
                        task_name: taskElement.task_name,
                        grade: gradeElement.grade,
                        count: gradeElement.count
                    };
                });
            });
        });
    };

    return GradeCountStatistic;
})();

const tabToStatistic = {
    "gradeCount": new GradeCountStatistic("statisticsGradeDiv"),
    "gradeDistribution": new GradeDistributionStatistic("statisticsGradeDistributionDiv"),
    "submissionsVerdict": new SubmissionsVerdictStatistic("submissionsVerdictDiv"),
    "bestSubmissionsVerdict": new BestSubmissionsVerdictStatistic("bestSubmissionsVerdictDiv"),
};

$(function () {
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        const statistic = tabToStatistic[e.target.getAttribute("aria-controls")];

        if (statistic) {
            statistic.plotAsync();
        }
    });
    $('.active > a[data-toggle="tab"]').trigger('shown.bs.tab');
});
