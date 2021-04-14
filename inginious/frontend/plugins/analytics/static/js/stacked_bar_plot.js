const StackedBarPlot = (function () {
    function BarPlot() {
        this.divId = "analyticsPerCoursePlot";
        this.requestUrl = "/api/stacked_bar_plot_analytics/";
    }

    BarPlot.prototype = Object.create(AnalyticsDiagram.prototype);
    BarPlot.prototype._generate_plot_layout = function (annotation) {
        return {
            barmode: "stack",
            annotations: annotation,
            showlegend: true,
            plot_bgcolor: "#F3F3F3",
            paper_bgcolor: "#F3F3F3"
        };
    };
    BarPlot.prototype._generateTraces = function (xData, yData, services) {
        function generateTrace(xData, courseYData, serviceName, color) {
            return {
                x: xData,
                y: courseYData,
                name: serviceName,
                type: "bar",
                marker: {
                    color: color
                }
            };
        }

        let dataToPlot = [];
        const colorScale = d3.scale.linear().domain([0, 0.5, 1]).range(["red", "yellow", "green"]);
        $.each(services, function (index, serviceName) {
            let color = colorScale(index * (1.0 / services.length));
            let trace = generateTrace(xData, yData[index], serviceName, color);
            dataToPlot.push(trace);
        });
        return dataToPlot;

    }
    BarPlot.prototype._plotData = function () {
        const _this = this;


        function createAnnotationArray(xData, originalYData) {
            const annotations = [];
            const totalLabels = originalYData.map((row) => row.reduce((a, b) => {
                return a + b;
            }, 0));
            $.each(xData, (index, name) => {
                annotations.push(createAnnotation(name, totalLabels[index]));
            });
            return annotations;
        }

        function createAnnotation(courseName, value) {
            return {
                x: courseName,
                y: value,
                text: value,
                xanchor: "center",
                yanchor: "bottom",
                showarrow: false
            }
        }

        function transpose(matrix) {
            if (matrix.length !== 0) {
                return matrix[0].map((_, colIndex) => matrix.map((row) => row[colIndex]));
            }else {
                return [];
            }
        }

        Plotly.d3.json(generate_get_url_plot(_this.requestUrl), function (error, data) {
            const xData = getCoursesNames(data["x_data"]);
            const yData = transpose(data["y_data"]);
            const services = get_services_names(data["services"]);
            const traces = _this._generateTraces(xData, yData, services);
            const annotation = createAnnotationArray(xData, data["y_data"]);
            const layout = _this._generate_plot_layout(annotation);

            Plotly.newPlot(_this.divId, traces, layout);
        });

    }

    return BarPlot;
}());