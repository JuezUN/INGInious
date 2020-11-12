function get_service_name_by_key(key) {
    return all_services[key];
}

function get_services_names(services = []) {
    return services.map(value => {
        return get_service_name_by_key(value);
    });
}

function generate_get_url_plot(path) {
    const request = [path];
    const parameters = [];

    const analytics_username_filter = $("#analytics_username").val();
    const analytics_start_date_filter = $("#analytics_date").val();
    const analytics_service_filter = $("#analytics_service").val();
    const analytics_course_filter = $("#analytics_course").val();

    if (analytics_username_filter || analytics_start_date_filter || analytics_service_filter || analytics_course_filter)
        request.push("?");
    if (analytics_username_filter)
        parameters.push('username=' + analytics_username_filter);
    if (analytics_service_filter)
        parameters.push('service=' + analytics_service_filter);
    if (analytics_start_date_filter)
        parameters.push('start_date=' + analytics_start_date_filter);
    if (analytics_course_filter)
        parameters.push('course_id=' + analytics_course_filter);
    request.push(parameters.join('&'));
    return request.join('');
}

function on_search() {
    $('.active > a[data-toggle="tab"]').trigger('shown.bs.tab');
}

function parse_str_to_date(str_date){
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

$(function () {

    const tabToAnalyticsPlot = {
        "heat-map-tab": new HeatMap(),
        "plot-visits-per-day-tab": new VisitsPerDayChart(),
        "box-plot-tab": new BoxPlot(),
        "radar-plot-tab": new RadarPlot()
    };
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        const analytics_plot = tabToAnalyticsPlot[e.target.id];
        if (analytics_plot) {
            analytics_plot.plot();
        }
    });
    $('.active > a[data-toggle="tab"]').trigger('shown.bs.tab');

    $('#analytics_date_filter').datetimepicker({locale: 'en', sideBySide: true, maxDate: moment(), format:'YYYY-MM-DD'});

    $("#analytics_date").val(`${new Date().getFullYear()}-01-02`);
    $("#analytics_service").val("");
});
