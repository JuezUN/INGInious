function get_service_name_by_key(key) {
    return all_services[key];
}

function get_services_names(services = []) {
    return services.map(value => {
        return get_service_name_by_key(value);
    });
}

function getCourseNameByKey(key) {
    return all_courses[key];
}

function getCoursesNames(services = []) {
    return services.map(value => {
        return getCourseNameByKey(value);
    });
}

function generate_get_url_plot(path) {
    const request = [path];
    const parameters = [];

    const analytics_username_filter = $("#analytics_username").val();
    const analytics_start_date_filter = $("#analytics_from_date").val();
    const analytics_end_date_filter = $("#analytics_to_date").val();
    const analytics_service_filter = $("#analytics_service").val();
    const analytics_course_filter = $("#analytics_course").val();

    if (analytics_username_filter || analytics_start_date_filter || analytics_end_date_filter
        || analytics_service_filter || analytics_course_filter) {
        request.push("?");
    }
    if (analytics_username_filter)
        parameters.push('username=' + analytics_username_filter);
    if (analytics_service_filter)
        parameters.push('service=' + analytics_service_filter);
    if (analytics_start_date_filter)
        parameters.push('start_date=' + analytics_start_date_filter);
    if (analytics_end_date_filter)
        parameters.push('end_date=' + analytics_end_date_filter);
    if (analytics_course_filter)
        parameters.push('course_id=' + analytics_course_filter);
    request.push(parameters.join('&'));
    return request.join('');
}

function updateDataFilters() {
    $(".active > a[data-toggle=\"tab\"]").trigger("shown.bs.tab");
}

function parse_str_to_date(str_date) {
    return new Date(str_date);
}

const AnalyticsDiagram = (function () {
    function AnalyticsDiagram() {
        this._cachedPromise = null;
    }

    AnalyticsDiagram.prototype.plot = function () {
        this._plotData();
    };

    AnalyticsDiagram.prototype._plotData = function () {
        throw 'Not implemented';
    };

    return AnalyticsDiagram;
})();

function getAllAnalytics() {
    const apiPath = "/api/analytics/";
    return $.get(generate_get_url_plot(apiPath), function (result) {
        exportCSVFile(result, "analytics");
    }, "json").fail(function () {

    });
}

function exportCSVFile(items, fileTitle) {
    const filename = `${fileTitle}.csv`;
    const csv = "data:text/csv;charset=utf-8," + Papa.unparse(items);
    const data = encodeURI(csv);
    const link = document.createElement("a");

    link.setAttribute("href", data);
    link.setAttribute("download", filename);

    // Append link to the body in order to make it work on Firefox.
    document.body.appendChild(link);

    link.click();
    link.remove();
}

function turnStringNumberToTwoDigitFormat(date) {
    // turn 1 to 01 for example, but 10 is still 10
    return date.toString().padStart(2, "0");
}

function setupDatetimePicker() {
    const fromDateFilter = $("#analytics_from_date_filter");
    const toDateFilter = $("#analytics_to_date_filter");
    fromDateFilter.datetimepicker({
        locale: "en",
        sideBySide: true,
        maxDate: moment(),
        format: "YYYY-MM-DD"
    });
    toDateFilter.datetimepicker({
        locale: "en",
        sideBySide: true,
        maxDate: moment(),
        format: "YYYY-MM-DD"
    });

    fromDateFilter.on("dp.change", function () {
        const minDate = $("#analytics_from_date").val();
        toDateFilter.data("DateTimePicker").minDate(minDate);
    });
    updateDate()
}

function updateDate() {
    const date = new Date();
    const fromDate = $("#analytics_from_date");
    fromDate.val(`${date.getFullYear()}-01-02`);
    fromDate.trigger("dp.change");
    $("#analytics_to_date")
        .val(`${date.getFullYear()}-${turnStringNumberToTwoDigitFormat((date.getMonth() + 1))}-${turnStringNumberToTwoDigitFormat(date.getDate())}`);
}

function setupServiceAndCourseFilter() {
    const course = $("#analytics_course");
    const service = $("#analytics_service");

    function changeSpan(id, value) {
        $(`#${id} [class="ms-select-all"] span`).html(`[${value}]`);
    }

    course.multipleSelect(
        {
            maxHeight: 140,
            onClick: function (view) {
                if (!view.selected) {
                    changeSpan("courseCol", "Select all");
                }
            },
            onCheckAll: function () {
                changeSpan("courseCol", "Deselect all");
            },
            onUncheckAll: function () {
                changeSpan("courseCol", "Select all");
            },
            onAfterCreate: function () {
                course.multipleSelect("uncheckAll")
            }
        });
    service.multipleSelect(
        {
            maxHeight: 140,
            onClick: function (view) {
                if (!view.selected) {
                    changeSpan("serviceCol", "Select all");
                }
            },
            onCheckAll: function () {
                changeSpan("serviceCol", "Deselect all");

            },
            onUncheckAll: function () {
                changeSpan("serviceCol", "Select all");
            },
            onAfterCreate: function () {
                service.multipleSelect("uncheckAll");
            }
        });
}

function setupTabs() {
    const tabToAnalyticsPlot = {
        "heat-map-tab": new HeatMap(),
        "plot-visits-per-day-tab": new VisitsPerDayChart(),
        "box-plot-tab": new BoxPlot(),
        "radar-plot-tab": new RadarPlot(),
        "bar-plot-tab": new StackedBarPlot()
    };
    $("a[data-toggle=\"tab\"]").on("shown.bs.tab", function (e) {
        const analytics_plot = tabToAnalyticsPlot[e.target.id];
        if (analytics_plot) {
            analytics_plot.plot();
        }
    });
}

$(function () {
    setupTabs();
    setupDatetimePicker();
    setupServiceAndCourseFilter();
    updateDataFilters()
});
