const RadarPlot = (function () {
    function RadarPlot() {
        this.div_id = "analytics_radar_plot";
        this._radar_request = "/api/analytics/";
    }

    RadarPlot.prototype = Object.create(AnalyticsDiagram.prototype);

    RadarPlot.prototype._plotData = function () {
        const _this = this;
        Plotly.d3.json(generate_get_url_plot(_this._radar_request), function (err, rows) {
            const services_visits = {};

            rows.forEach((item, _) => {
                if (item.service in services_visits)
                    services_visits[item.service] += 1;
                else
                    services_visits[item.service] = 1;
            });

            const services = Object.keys(services_visits);
            const visits = services.map((service) => {
                return services_visits[service];
            });

            // Add the first element for visualization
            services.push(services[0]);
            visits.push(visits[0]);

            const data = [
                {
                    type: 'scatterpolar',
                    r: visits,
                    theta: get_services_names(services),
                    fill: 'toself',
                    name: 'Group A'
                }
            ];

            const layout = {
                polar: {
                    radialaxis: {
                        visible: true,
                        range: [0, Math.max.apply(this, visits)]
                    }
                }
            };

            Plotly.newPlot(_this.div_id, data, layout, {showSendToCloud: true})
        });
    };

    return RadarPlot;
}());
