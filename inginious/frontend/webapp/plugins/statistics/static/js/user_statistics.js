function plotTriesPerTasks(tries_per_tasks) {
    var SUBMISSIONS_COUNT_TO_PIXELS = getRatio(tries_per_tasks);

    var results =
        [
            "COMPILATION_ERROR",
            "TIME_LIMIT_EXCEEDED",
            "MEMORY_LIMIT_EXCEEDED",
            "RUNTIME_ERROR",
            "WRONG_ANSWER",
            "INTERNAL_ERROR",
            "ACCEPTED"
        ];


    var resultsDict = {};

    for (var index = 0; index < results.length; index++) {
        resultsDict[results[index]] =
            {
                "mode": "markers",
                "name": results[index],
                "marker":
                    {
                        "sizemode": "area",
                        "sizeref": SUBMISSIONS_COUNT_TO_PIXELS,
                        "size": []
                    },
                "text": [],
                "x": [],
                "y": []
            }
    }


    for (var index = 0; index < tries_per_tasks.length; index++) {
        for (var j = 0; j < results.length; j++) {
            if (tries_per_tasks[index].result === results[j]) {
                resultsDict[results[j]]["x"].push(tries_per_tasks[index].taskid);
                resultsDict[results[j]]["y"].push(tries_per_tasks[index].grade);
                resultsDict[results[j]]["text"].push(tries_per_tasks[index].tried + " submissions");
                resultsDict[results[j]]["marker"]["size"].push(tries_per_tasks[index].tried);
            }
        }
    }

    var data = [];
    for (var index = 0; index < results.length; index++) {
        data.push(resultsDict[results[index]]);
    }

    var layout = {
        xaxis: {title: 'Task'},
        yaxis: {title: 'Grade', range: [-10, 110]},
        margin: {t: 20},
        hovermode: 'closest'
    };
    Plotly.plot('tries_per_task', data, layout, {showLink: false});
}

function getRatio(tries_per_tasks) {
    var sum = 0.0;

    for(var i = 0 ; i < tries_per_tasks.length ; i++){
        sum += tries_per_tasks[i].tried;
    }

    var avg = sum / tries_per_tasks.length;
    return avg / 1000;
}
