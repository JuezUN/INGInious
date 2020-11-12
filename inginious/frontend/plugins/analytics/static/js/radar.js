const RadarPlot = (function () {
    function RadarPlot() {
        this.div_id = "analytics_radar_plot";
        this._radar_request = "/api/radar_plot_analytics/";
    }

    RadarPlot.prototype = Object.create(AnalyticsDiagram.prototype);

    RadarPlot.prototype._plotData = function () {
        const _this = this;
        Plotly.d3.json(generate_get_url_plot(_this._radar_request), function (err, data) {
            const services = data['services'];
            const visits = data['visits'];
            // Add the first element for visualization
            services.push(services[0]);
            visits.push(visits[0]);
            const plot_data = [
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

            Plotly.newPlot(_this.div_id, plot_data, layout, {showSendToCloud: true})
        });
    };

    return RadarPlot;
}());
