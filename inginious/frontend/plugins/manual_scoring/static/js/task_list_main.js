const DOWNLOAD_CSV_BTN_ID = "download_csv";
const RESULT_INFO_AREA_ID = "information_area";

function getManualScoringInfo(course_id) {
    const contentDanger = "Error getting the information. Try later";
    return $.get(`/api/manual_scoring/${course_id}`, function (result) {
        exportCSVFile(result, "test");
    }, "json").fail(function () {
        new MessageBox(RESULT_INFO_AREA_ID, contentDanger, "danger", false);
    });
}

function exportCSVFile(items, fileTitle) {
    const filename = `${fileTitle}.csv`;
    const csv = 'data:text/csv;charset=utf-8,' + Papa.unparse(items);
    const data = encodeURI(csv);
    const link = document.createElement('a');

    link.setAttribute('href', data);
    link.setAttribute('download', filename);

    // Append link to the body in order to make it work on Firefox.
    document.body.appendChild(link);

    link.click();
    link.remove();
}


function addListenerToDownloadButton() {
    const course = getCourseId();
    $(`#${DOWNLOAD_CSV_BTN_ID}`).click(function () {
        getManualScoringInfo(course);
    });
}

jQuery(document).ready(function () {
    addListenerToDownloadButton()
});