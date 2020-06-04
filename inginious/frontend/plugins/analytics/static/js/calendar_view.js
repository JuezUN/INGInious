const HeatMap = (function () {
    function HeatMap() {
        this.div_id = "analytics_heat_map_calendar";
        this._calendar_request = "/api/analytics/";
        this.color = d3.scale.linear().range(['#ebedf0', '#e2e45b', '#196127']).domain([0, 0.5, 1]);
        this.width = 900;
        this.height = 105;
        this.cellSize = 12; // cell size
        this.week_days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        this.month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        this.day = d3.time.format("%w");
        this.week = d3.time.format("%U");
        this.percent = d3.format(".1%");
        this.format = d3.time.format("%Y%m%d");

        this.start_year = (new Date).getFullYear();
    }

    HeatMap.prototype = Object.create(AnalyticsDiagram.prototype);

    HeatMap.prototype.update_year = function(){
        this.start_year = Number(parse_str_to_date($('#analytics_date').val()).getFullYear()) - 1;
        if (!this.start_year){
            this.start_year = (new Date).getFullYear() - 1;
        }
    };

    HeatMap.prototype._get_svg = function () {
        const _this = this;

        function _monthPath(t0) {
            const t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
                d0 = +_this.day(t0), w0 = +_this.week(t0),
                d1 = +_this.day(t1), w1 = +_this.week(t1);
            return "M" + (w0 + 1) * _this.cellSize + "," + d0 * _this.cellSize
                + "H" + w0 * _this.cellSize + "V" + 7 * _this.cellSize
                + "H" + w1 * _this.cellSize + "V" + (d1 + 1) * _this.cellSize
                + "H" + (w1 + 1) * _this.cellSize + "V" + 0
                + "H" + (w0 + 1) * _this.cellSize + "Z";
        }

        const svg = d3.select("#" + this.div_id).selectAll("svg")
            .data(d3.range((new Date).getFullYear(), this.start_year, -1))
            .enter().append("svg")
            .attr("width", '100%')
            .attr("data-height", '0.5678')
            .attr("viewBox", '0 0 900 105')
            .attr("class", "RdYlGn")
            .append("g")
            .attr("transform", "translate(" + ((this.width - this.cellSize * 53) / 2) + "," + (this.height - this.cellSize * 7 - 1) + ")");


        svg.append("text")
            .attr("transform", "translate(-38," + this.cellSize * 3.5 + ")rotate(-90)")
            .style("text-anchor", "middle")
            .text(function (d) {
                return d;
            });

        for (let i = 0; i < 7; i++) {
            svg.append("text")
                .attr("transform", "translate(-5," + this.cellSize * (i + 1) + ")")
                .style("text-anchor", "end")
                .attr("dy", "-.25em")
                .text(function (d) {
                    return _this.week_days[i];
                });
        }

        svg.selectAll(".month")
            .data(function (d) {
                return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1));
            })
            .enter().append("path")
            .attr("class", "month")
            .attr("id", function (d, i) {
                return _this.month[i]
            })
            .attr("d", _monthPath);

        const legend = svg.selectAll(".legend")
            .data(_this.month)
            .enter().append("g")
            .attr("class", "legend")
            .attr("transform", function (d, i) {
                return "translate(" + (((i + 1) * 50) + 8) + ",0)";
            });

        legend.append("text")
            .attr("class", function (d, i) {
                return _this.month[i]
            })
            .style("text-anchor", "end")
            .attr("dy", "-.25em")
            .text(function (d, i) {
                return _this.month[i]
            });
        return svg;
    };

    HeatMap.prototype._get_rect = function () {
        const _this = this;
        this.update_year();
        const svg = this._get_svg();
        return svg.selectAll(".day")
            .data(function (d) {
                return d3.time.days(new Date(d, 0, 1), new Date(d + 1, 0, 1));
            })
            .enter()
            .append("rect")
            .attr("class", "day")
            .attr("width", this.cellSize)
            .attr("height", this.cellSize)
            .attr("x", function (d) {
                return _this.week(d) * _this.cellSize;
            })
            .attr("y", function (d) {
                return _this.day(d) * _this.cellSize;
            })
            .attr("fill", '#fff')
            .attr("onclick", function (d) {
                return "console.log(" + _this.week(d) + ");"
            })
            .datum(this.format);
    };

    HeatMap.prototype._plotData = function () {
        const _this = this;
        $('#' + this.div_id).html("");
        d3.json(generate_get_url_plot(_this._calendar_request), function (error, csv) {
            const visits = {};
            const visits_for_table = {};

            csv.forEach(function (item, _) {
                let date = new Date(item.date);
                date.setHours(0);
                date.setMinutes(0);
                date.setSeconds(0);
                date = date.toISOString().slice(0, 10);
                if (date in visits) {
                    visits[date] += 1
                } else {
                    visits[date] = 1;
                    visits_for_table[date] = []
                }
                visits_for_table[date].push(item);
            });

            // Complete the dates
            let today = new Date();
            today.setDate(today.getDate() + 1);
            let date_start = new Date();

            date_start.setFullYear(_this.start_year);
            date_start.setMonth(0);
            date_start.setDate(0);

            today = today.toISOString().slice(0, 10);
            let day = date_start.toISOString().slice(0, 10);

            const visits_arr = [];
            while (day !== today) {
                if (day in visits)
                    visits_arr.push({date: day.replace(/\-/g, ''), visits: visits[day]});
                else
                    visits_arr.push({date: day.replace(/\-/g, ''), visits: 0});

                day = new Date(day);
                day.setDate(day.getDate() + 1);
                day = day.toISOString().slice(0, 10);
            }

            const visits_max = d3.max(visits_arr, function (d) {
                return d.visits;
            });

            const data = d3.nest()
                .key(function (d) {
                    return d.date;
                })
                .rollup(function (d) {
                    return Math.sqrt(visits_max > 0 ? d[0].visits / visits_max : 0);
                })
                .map(visits_arr);

            _this._get_rect().filter(function (d) {
                return d in data;
            })
                .attr("fill", function (d) {
                    return _this.color(data[d]);
                })
                .attr("data-title", function (d) {
                    return d.slice(0, 4) + "-" + d.slice(4, 6) + "-" + d.slice(6, 8) + " " + "visits : " +
                        (visits[d.slice(0, 4) + "-" + d.slice(4, 6) + "-" + d.slice(6, 8)] ? visits[d.slice(0, 4) + "-" +
                        d.slice(4, 6) + "-" + d.slice(6, 8)] : 0)
                });
            $("rect").tooltip({container: 'body', html: true, placement: 'top'});
        });
    };

    return HeatMap
}());
