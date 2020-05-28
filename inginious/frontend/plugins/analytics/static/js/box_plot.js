const BoxPlot = (function () {
    function BoxPlot() {
        this.div_id = "analytics_box_plot";
        this.request_url = "/api/analytics/";
    }

    BoxPlot.prototype = Object.create(AnalyticsDiagram.prototype);

    BoxPlot.prototype._parse_date = function(date){
        const new_date = new Date(date);
        new_date.setHours(0);
        new_date.setMinutes(0);
        new_date.setSeconds(0);
        new_date.setMilliseconds(0);
        return new_date.toISOString();
    };

    BoxPlot.prototype._get_visits_by_service = function (data) {
        const visits_by_service = {};
        data.forEach((item, _) => {
            // Object: Service - Date -> number_of_visits
            const date = this._parse_date(item.date);

            if (!(item.service in visits_by_service)) {
                visits_by_service[item.service] = {};

            }
            if (!(date in visits_by_service[item.service])) visits_by_service[item.service][date] = 0;

            visits_by_service[item.service][date] += 1;
        });
        return visits_by_service;
    };

    BoxPlot.prototype._get_all_dates = function (data) {
        const dates = {};
        data.forEach((item, _) => {
            const date = this._parse_date(item.date);
            dates[date] = 0;
        });
        return Object.keys(dates);
    };

    BoxPlot.prototype._generate_plot_layout = function () {
        return {
            title: 'Box plot of used services',
            yaxis: {
                autorange: true,
                showgrid: true,
                zeroline: true,
                dtick: 5,
                gridcolor: 'rgb(255, 255, 255)',
                gridwidth: 1,
                zerolinecolor: 'rgb(255, 255, 255)',
                zerolinewidth: 2
            },
            margin: {
                l: 40,
                r: 30,
                b: 80,
                t: 100
            },
            paper_bgcolor: 'rgb(243, 243, 243)',
            plot_bgcolor: 'rgb(243, 243, 243)',
            showlegend: false
        };
    };

    BoxPlot.prototype._plotData = function () {
        const _this = this;
        Plotly.d3.json(generate_get_url_plot(_this.request_url), function (err, rows) {
            const services_visits = _this._get_visits_by_service(rows);
            const dates = _this._get_all_dates(rows);

            const xData = Object.keys(services_visits);
            const yData = [];
            xData.forEach((service, _) => {
                const info = [];
                dates.forEach((date, _) => {
                    if (date in services_visits[service]){
                        info.push(services_visits[service][date]);
                    } else {
                        info.push(0);
                    }
                });
                yData.push(info);
            });

            const data = [];
            for (let i = 0; i < xData.length; i++) {
                const result = {
                    type: 'box',
                    y: yData[i],
                    name: get_service_name_by_key(xData[i]),
                    jitter: 0.5,
                    whiskerwidth: 0.2,
                    fillcolor: 'cls',
                    marker: {
                        size: 2
                    },
                    line: {
                        width: 1
                    }
                };
                data.push(result);
            }

            const layout = _this._generate_plot_layout();
            Plotly.newPlot(_this.div_id, data, layout, {showSendToCloud: true});
        });
    };

    return BoxPlot;
}());


