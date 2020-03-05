const username = document.getElementById("student_username").value;
const service = document.getElementById('service').value;
parameters = [];

let request = "/api/analytics_consult/";
if (username || service)
    request += "?";
if (username)
    parameters.push('username=' + username);
if (service)
    parameters.push('service=' + service);

request += parameters.join('&');

Plotly.d3.json(request, function (err, rows) {

    function unpack(rows, key) {
        return rows.map(function (row) {
            return row[key];
        });
    }

// visits -> key:date -> key:service -> key:visits -> int
    const visits = {};

    rows.forEach((item, _) => {
        let date = new Date(item.date);
        // Check for day, accumulate all to a day instead of hours:minutes:seconds
        date.setHours(0);
        date.setMinutes(0);
        date.setSeconds(0);
        date.setMilliseconds(0);
        let key = date.toISOString();
        if (!(key in visits))
            visits[key] = {};
        if (item.service in visits[key])
            visits[key][item.service] += 1;
        else
            visits[key][item.service] = 1;

    });

    const visits_keys_sorted = Object.keys(visits).sort();

    data = [];
    const data_by_service = {};
    visits_keys_sorted.forEach((str_date, _) => {
        // Sum over all the services
        let total_visits = 0;
        for (let service_visit in visits[str_date]) {
            total_visits += visits[str_date][service_visit];
            if (!(service_visit in data_by_service))
                data_by_service[service_visit] = [];
            data_by_service[service_visit].push({
                'date': str_date.slice(0, 10),
                'visits': visits[str_date][service_visit]
            })
        }

        let data_entry = {'date': str_date.slice(0, 10), 'visits': total_visits};
        data.push(data_entry);
    });

    // Colors
    const color_scale = d3.scale.linear().domain([0, 0.5, 1]).range(['red', 'yellow', 'green']);

    // Pass the information to the API
    const trace1 = {
        type: "scatter",
        mode: "lines",
        name: 'All',
        x: unpack(data, 'date'),
        y: unpack(data, 'visits'),
        line: {color: '#17BECF'}
    };

    const traces = {};

    let len_by_service = Object.keys(data_by_service).length;
    Object.keys(data_by_service).forEach((service, index) => {
        traces[service] = {
            type: "scatter",
            mode: "lines",
            name: service,
            x: unpack(data_by_service[service], 'date'),
            y: unpack(data_by_service[service], 'visits'),
            line: {color: color_scale(index * (1.0 / (len_by_service - 1)))}
        }
    });

    const data = [trace1];
    for (let service_visit in traces) {
        data.push(traces[service_visit]);
    }

    // Today
    const today = new Date();

    // First day of current year
    const first_day = new Date(today.getFullYear(), 0, 1);

    // Two months earlier
    let two_m_earlier = new Date(today);
    two_m_earlier.setMonth(two_m_earlier.getMonth() - 2);

    let layout = {
        title: 'Student visits by day',
        xaxis: {
            //autorange: true,
            range: [two_m_earlier.toISOString().slice(0, 10), (new Date()).toISOString().slice(0, 10)],
            rangeselector: {
                buttons: [
                    {
                        count: 1,
                        label: '1m',
                        step: 'month',
                        stepmode: 'backward'
                    },
                    {
                        count: 6,
                        label: '6m',
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

    Plotly.newPlot('myDiv', data, layout, {showSendToCloud: true});
});
