const VisitsPerDayChart = (function () {
    function VisitsPerDayChart() {
        this.div_id = "analytics_plot_visits_per_day";
        this._time_series_request = "/api/analytics/";
    }

    VisitsPerDayChart.prototype = Object.create(AnalyticsDiagram.prototype);

    VisitsPerDayChart.prototype._parse_time_series_data = function (data) {
        // visits -> key:date -> key:service -> key:visits -> int
        const visits = {};
        data.forEach((item, _) => {
            const date = new Date(item.date);
            // Check for day, accumulate all to a day instead of hours:minutes:seconds
            date.setHours(0);
            date.setMinutes(0);
            date.setSeconds(0);
            date.setMilliseconds(0);
            const key = date.toISOString();
            if (!(key in visits))
                visits[key] = {};
            if (item.service in visits[key])
                visits[key][item.service] += 1;
            else
                visits[key][item.service] = 1;
        });

        return visits
    };

    VisitsPerDayChart.prototype._get_data_by_service = function(data) {
        const data_by_service = {};
        const visits_keys_sorted = Object.keys(data).sort();
        visits_keys_sorted.forEach((str_date, _) => {
            // Sum over all the services
            for (let service in data[str_date]) {
                if (!(service in data_by_service))
                    data_by_service[service] = [];
                data_by_service[service].push({
                    'date': str_date.slice(0, 10),
                    'visits': data[str_date][service]
                })
            }
        });
        return data_by_service;
    };

    VisitsPerDayChart.prototype._get_data_by_day = function(data) {
        const data_by_day = [];
        const visits_keys_sorted = Object.keys(data).sort();
        visits_keys_sorted.forEach((str_date, _) => {
            // Sum over all the services
            let total_visits = 0;
            for (let service in data[str_date]) {
                total_visits += data[str_date][service];
            }

            const data_entry = {'date': str_date.slice(0, 10), 'visits': total_visits};
            data_by_day.push(data_entry);
        });
        return data_by_day;
    };

    VisitsPerDayChart.prototype._generate_traces = function(data_by_day, data_by_service){
        // Pass the information to the API
        const trace_all_services = {
            type: "scatter",
            mode: "lines",
            name: 'All',
            x: unpack(data_by_day, 'date'),
            y: unpack(data_by_day, 'visits'),
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

    VisitsPerDayChart.prototype._plotData = function(){
        const _this = this;
        Plotly.d3.json(generate_get_url_plot(_this._time_series_request), function (err, rows) {

            const visits = _this._parse_time_series_data(rows);
            const data_by_day = _this._get_data_by_day(visits);
            const data_by_service = _this._get_data_by_service(visits);

            const traces = _this._generate_traces(data_by_day, data_by_service);
            const today = new Date();

            // First day of current year
            const first_day = new Date(today.getFullYear(), 0, 1);

            // Two months earlier
            const two_m_earlier = new Date(today);
            two_m_earlier.setMonth(two_m_earlier.getMonth() - 2);

            let layout = {
                title: 'Visits per day',
                xaxis: {
                    //autorange: true,
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

