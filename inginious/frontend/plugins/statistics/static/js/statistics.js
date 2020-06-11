const CsvConverter = (function () {
    function CsvConverter(data) {
        this.data = data;
    }

    CsvConverter.prototype.downloadCsv = function () {
        const filename = 'export.csv';
        const csv = 'data:text/csv;charset=utf-8,' + Papa.unparse(this.data);
        const data = encodeURI(csv);
        const link = document.createElement('a');

        link.setAttribute('href', data);
        link.setAttribute('download', filename);

        // Append link to the body in order to make it work on Firefox.
        document.body.appendChild(link);

        link.click();
        link.remove();
    };

    return CsvConverter;
}());

const Statistic = (function () {
    function Statistic() {
        this._cachedPromise = null;
    }

    Statistic.prototype._fetchAndCacheData = function () {
        if (this._cachedPromise == null) {
            this._cachedPromise = this._fetchData();
        }

        return this._cachedPromise;
    };

    Statistic.prototype.plotAsync = function () {
        const statistic = this;
        this._fetchAndCacheData().then(function (data) {
            statistic._plotData(data);
        });
    };

    Statistic.prototype._fetchCsvData = function () {
        return this._fetchAndCacheData();
    };

    Statistic.prototype.downloadCsvAsync = function () {
        this._fetchCsvData().then(function (data) {
            const csvConverter = new CsvConverter(data);
            csvConverter.downloadCsv();
        });
    };

    Statistic.prototype._plotData = function (data) {
        throw 'Not implemented';
    };

    Statistic.prototype._fetchData = function () {
        throw 'Not implemented';
    };

    return Statistic;
})();

function createSubmissionLink(submissionId) {
    const urlTemplate = _.template("/submission/${ submissionId }");

    return urlTemplate({
        submissionId: submissionId
    });
}

function generateVerdictSubmissionTable(tableId, submissions) {
    const table = $("#" + tableId);

    table.html("<thead><tr><th>Username</th><th>Grade</th><th>Status</th><th>Summary result</th><th>Submitted on" +
        "</th><th>Submission</th></tr></thead>");
    const tableBody = $("<tbody/>");

    for (let i = 0; i < submissions.length; ++i) {
        const row = $("<tr/>");
        const entry = submissions[i];

        const cells = [entry.username, entry.grade, entry.status || '-', entry.summary_result || '-',
            entry.submitted_on || '-'];

        for (let j = 0; j < cells.length; ++j) {
            const cell = $("<td/>");
            cell.text(cells[j]);
            row.append(cell);
        }

        const submissionCell = $("<td/>");
        if (entry.id) {
            const submissionLink = $("<a>", {
                text: entry.id,
                href: createSubmissionLink(entry.id)
            });

            submissionCell.append(submissionLink);
        } else {
            submissionCell.text('No submission available');
        }

        row.append(submissionCell);

        tableBody.append(row);
    }

    table.append(tableBody);
}

function generateSubmissionTable(tableId, userTasks) {
    const table = $("#" + tableId);

    table.html("<thead><tr><th>Username</th><th>Grade</th><th>Status</th><th>Summary result</th><th>Submitted on" +
        "</th><th>Submission</th></tr></thead>");
    const tableBody = $("<tbody/>");

    for (let i = 0; i < userTasks.length; ++i) {
        const row = $("<tr/>");
        const entry = userTasks[i];
        const submission = entry.submission || {};

        const cells = [entry.username, entry.grade, submission.status || '-', submission.summary_result || '-',
            submission.submitted_on || '-'];

        for (let j = 0; j < cells.length; ++j) {
            const cell = $("<td/>");
            cell.text(cells[j]);
            row.append(cell);
        }

        const submissionCell = $("<td/>");
        if (submission.id) {
            const submissionLink = $("<a>", {
                text: submission.id,
                href: createSubmissionLink(submission.id)
            });

            submissionCell.append(submissionLink);
        } else {
            submissionCell.text('No submission available');
        }

        row.append(submissionCell);

        tableBody.append(row);
    }

    table.append(tableBody);
}

function createAlertHtml(alertClass, content) {
    const alertHtml = '<div class="alert ' + alertClass + ' alert-dismissible" role="alert">' +
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
        '<span aria-hidden="true">&times;</span></button>' + content + '</div>';

    return alertHtml;
}
