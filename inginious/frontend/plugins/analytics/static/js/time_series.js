const VisitsPerDayChart = (function () {
    function VisitsPerDayChart() {
        this.div_id = "analytics_plot_visits_per_day";
        this._time_series_request = "/api/time_series_plot_analytics/";
    }

    VisitsPerDayChart.prototype = Object.create(AnalyticsDiagram.prototype);

    VisitsPerDayChart.prototype._generate_traces = function (data_all_services, data_by_service) {
        // Pass the information to the API
        const trace_all_services = {
            type: "scatter",
            mode: "lines",
            name: 'All',
            x: data_all_services['dates'],
            y: data_all_services['counts'],
            line: {color: '#17BECF'}
        };

        const services_traces = {};
        const color_scale = d3.scale.linear().domain([0, 0.5, 1]).range(['red', 'yellow', 'green']);

        let len_by_service = Object.keys(data_by_service).length;
        Object.keys(data_by_service).forEach((service, index) => {
            services_traces[service] = {
                type: "scatter",
                mode: "lines",
                name: get_service_name_by_key(service),
                x: unpack(data_by_service[service], 'date'),
                y: unpack(data_by_service[service], 'visits'),
                line: {color: color_scale(index * (1.0 / (len_by_service - 1)))}
            }
        });

        const traces = [trace_all_services];
        for (let service in services_traces) {
            traces.push(services_traces[service]);
        }
        return traces;
    };

    VisitsPerDayChart.prototype._plotData = function () {
        const _this = this;
        Plotly.d3.json(generate_get_url_plot(_this._time_series_request), function (err, visits) {
            const data_all_services = visits['data_all_services'];
            const data_by_service = visits['data_by_service'];

            const traces = _this._generate_traces(data_all_services, data_by_service);
            const today = new Date();

            // First day of current year
            const first_day = new Date(today.getFullYear(), 0, 1);

            // Two months earlier
            const two_m_earlier = new Date(today);
            two_m_earlier.setMonth(two_m_earlier.getMonth() - 2);

            let layout = {
                title: 'Visits per day',
                xaxis: {
                    autorange: true,
                    range: [two_m_earlier.toISOString().slice(0, 10), (new Date()).toISOString().slice(0, 10)],
                    rangeselector: {
                        buttons: [
                            {
                                count: 1,
                                label: '1 month',
                                step: 'month',
                                stepmode: 'backward'
                            },
                            {
                                count: 6,
                                label: '6 months',
                                step: 'month',
                                stepmode: 'backward'
                            },
                            {step: 'all'}
                        ]
                    },
                    rangeslider: {range: [first_day, (new Date()).toISOString().slice(0, 10)]},
                    type: 'date'
                },
                yaxis: {
                    autorange: true,
                    type: 'linear'
                }
            };

            Plotly.newPlot(_this.div_id, traces, layout, {showSendToCloud: true});
        });
    };

    return VisitsPerDayChart;
}());

function unpack(rows, key) {
    return rows.map(function (row) {
        return row[key];
    });
}

