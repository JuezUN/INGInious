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

function on_search() {
    $('.active > a[data-toggle="tab"]').trigger('shown.bs.tab');
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

function getAllAnalytics(course_id) {
    const contentDanger = "Error getting the information. Try later";
    const apiPath = "/api/analytics/";
    return $.get(generate_get_url_plot(apiPath), function (result) {
        exportCSVFile(result, "analytics");
    }, "json").fail(function () {

    });
}

function exportCSVFile(items, fileTitle) {
    const filename = `${fileTitle}.csv`;
    const csv = 'data:text/csv;charset=utf-8,' + Papa.unparse(items);
    const data = encodeURI(csv);
    const link = document.createElement('a');

    link.setAttribute('href', data);
    link.setAttribute('download', filename);

    // Append link to the body in order to make it work on Firefox.
    document.body.appendChild(link);

    link.click();
    link.remove();
}

function date_two_digit_format(date) {
    return date.toString().padStart(2, "0");
}

$(function () {

    const tabToAnalyticsPlot = {
        "heat-map-tab": new HeatMap(),
        "plot-visits-per-day-tab": new VisitsPerDayChart(),
        "box-plot-tab": new BoxPlot(),
        "radar-plot-tab": new RadarPlot(),
        "bar-plot-tab": new StackedBarPlot()
    };
    const date = new Date()
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        const analytics_plot = tabToAnalyticsPlot[e.target.id];
        if (analytics_plot) {
            analytics_plot.plot();
        }
    });
    $('.active > a[data-toggle="tab"]').trigger('shown.bs.tab');

    $('#analytics_from_date_filter').datetimepicker({
        locale: 'en',
        sideBySide: true,
        maxDate: moment(),
        format: 'YYYY-MM-DD'
    });
    $('#analytics_to_date_filter').datetimepicker({
        locale: 'en',
        sideBySide: true,
        maxDate: moment(),
        format: 'YYYY-MM-DD'
    });

    $("#analytics_from_date").val(`${date.getFullYear()}-01-02`);
    $("#analytics_to_date")
        .val(`${date.getFullYear()}-${date_two_digit_format((date.getMonth() + 1))}-${date_two_digit_format(date.getDate())}`);
    $("#analytics_course").multipleSelect({maxHeight: 140});
    $("#analytics_service").multipleSelect({maxHeight: 140});
});
