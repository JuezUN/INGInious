const BoxPlot = (function () {
    function BoxPlot() {
        this.div_id = "analytics_box_plot";
        this.request_url = "/api/box_plot_analytics/";
    }

    BoxPlot.prototype = Object.create(AnalyticsDiagram.prototype);

    BoxPlot.prototype._generatePlotLayout = function () {
        return {
            title: 'Box plot of used services',
            yaxis: {
                autorange: true,
                showgrid: true,
                zeroline: true,
                tickmode: 'auto',
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
        Plotly.d3.json(generate_get_url_plot(_this.request_url), function (err, data) {
            const x_data = data['x_data'];
            const y_data = data['y_data'];

            const plot_data = [];
            for (let i = 0; i < x_data.length; i++) {
                const result = {
                    type: 'box',
                    y: y_data[i],
                    name: get_service_name_by_key(x_data[i]),
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
                plot_data.push(result);
            }

            const layout = _this._generatePlotLayout();
            Plotly.newPlot(_this.div_id, plot_data, layout, {showSendToCloud: true});
        });
    };

    return BoxPlot;
}());


