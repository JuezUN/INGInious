

var width = 900,
height = 105,
cellSize = 12; // cell size
week_days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    
var day = d3.time.format("%w"),
    week = d3.time.format("%U"),
    percent = d3.format(".1%"),
    format = d3.time.format("%Y%m%d");
    parseDate = d3.time.format("%Y%m%d").parse;
        
var no_se = ["white",  '#002b53'];
var color = d3.scale.linear().range(['grey', 'yellow', 'green'])
    .domain([0, 0.5,  1])
    
let start_year = (new Date).getFullYear()  - Number(document.getElementById('duration_time').value);
var svg = d3.select(".calender-map").selectAll("svg")
    .data(d3.range((new Date).getFullYear(), start_year , -1))
.enter().append("svg")
    .attr("width", '100%')
    .attr("data-height", '0.5678')
    .attr("viewBox",'0 0 900 105')
    .attr("class", "RdYlGn")
.append("g")
    .attr("transform", "translate(" + ((width - cellSize * 53) / 2) + "," + (height - cellSize * 7 - 1) + ")");


svg.append("text")
    .attr("transform", "translate(-38," + cellSize * 3.5 + ")rotate(-90)")
    .style("text-anchor", "middle")
    .text(function(d) { return d; });

for (var i=0; i<7; i++)
{    
svg.append("text")
    .attr("transform", "translate(-5," + cellSize*(i+1) + ")")
    .style("text-anchor", "end")
    .attr("dy", "-.25em")
    .text(function(d) { return week_days[i]; }); 
}

var rect = svg.selectAll(".day")
    .data(function(d) { return d3.time.days(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
.enter()
    .append("rect")
    .attr("class", "day")
    .attr("width", cellSize)
    .attr("height", cellSize)
    .attr("x", function(d) { return week(d) * cellSize; })
    .attr("y", function(d) { return day(d) * cellSize; })
    .attr("fill",'#fff')
    .attr("onclick",function(d){ return "console.log(" +  week(d) + ");" } )
    .datum(format);

var legend = svg.selectAll(".legend")
    .data(month)
    .enter().append("g")
    .attr("class", "legend")
    .attr("transform", function(d, i) { return "translate(" + (((i+1) * 50)+8) + ",0)"; });

legend.append("text")
.attr("class", function(d,i){ return month[i] })
.style("text-anchor", "end")
.attr("dy", "-.25em")
.text(function(d,i){ return month[i] });

svg.selectAll(".month")
    .data(function(d) { return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
.enter().append("path")
    .attr("class", "month")
    .attr("id", function(d,i){ return month[i] })
    .attr("d", monthPath);


var username = document.getElementById("student_username").value;
var service = document.getElementById('service').value;
parameters = [];

var request = "/api/analytics_consult/";
if(username || service)
    request += "?"
if(username)
    parameters.push('username=' + username)
if(service)
    parameters.push('service=' + service)

request += parameters.join('&')

d3.json(request, function(error, csv) {

    visits = {}
    visits_for_table = {}

    csv.forEach(function(item, index) {
        let date = new Date(item.date);                
        date.setHours(0); date.setMinutes(0); date.setSeconds(0)
        date = date.toISOString().slice(0, 10);
        if( date in visits ){
            visits[date] += 1
        }
        else{
            visits[date] = 1
            visits_for_table[date] = []
        }
        visits_for_table[date].push(item);
    })



    // Complete the dates
    let today = new Date();
    today.setDate( today.getDate() + 1 );
    let date_start = new Date();

    date_start.setFullYear(start_year);date_start.setMonth(0); date_start.setDate(0);

    today = today.toISOString().slice(0, 10)
    let day = date_start.toISOString().slice(0, 10)

    visits_arr = []
    while( day !== today ){
        if( day in visits )
            visits_arr.push( { date: day.replace(/\-/g, ''), visits: visits[day] } )
        else    
            visits_arr.push(  { date: day.replace(/\-/g, ''), visits: 0 } )

        day = new Date(day)
        day.setDate( day.getDate() + 1 )
        day = day.toISOString().slice(0, 10)
    }

    console.log(visits_arr);
    var visits_max = d3.max(visits_arr, function(d) { return d.visits; });

    var data = d3.nest()
        .key(function(d) { return d.date; })
        .rollup(function(d) { return  Math.sqrt( visits_max > 0 ? d[0].visits / visits_max : 0); })
        .map(visits_arr);

    
    
    rect.filter(function(d) { return d in data; })
        .attr("fill", function(d) { return color(data[d]); })
        .attr("data-title", function(d) { return d.slice(0, 4) + "-" + d.slice(4, 6) + "-" + d.slice(6, 8) + " " +"visits : "+ (visits[d.slice(0, 4) + "-" + d.slice(4, 6) + "-" + d.slice(6, 8)] ? visits[d.slice(0, 4) + "-" + d.slice(4, 6) + "-" + d.slice(6, 8)]: 0)});   
        $("rect").tooltip({container: 'body', html: true, placement:'top'}); 
});

function numberWithCommas(x) {
    x = x.toString();
    var pattern = /(-?\d+)(\d{3})/;
    while (pattern.test(x))
        x = x.replace(pattern, "$1,$2");
    return x;
}

function monthPath(t0) {
var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
    d0 = +day(t0), w0 = +week(t0),
    d1 = +day(t1), w1 = +week(t1);
return "M" + (w0 + 1) * cellSize + "," + d0 * cellSize
    + "H" + w0 * cellSize + "V" + 7 * cellSize
    + "H" + w1 * cellSize + "V" + (d1 + 1) * cellSize
    + "H" + (w1 + 1) * cellSize + "V" + 0
    + "H" + (w0 + 1) * cellSize + "Z";
}
    
