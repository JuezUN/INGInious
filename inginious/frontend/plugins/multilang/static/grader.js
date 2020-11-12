// Function called in he returned feedback from submission
function updateDiffBlock(blockId, text) {
    let block = $("#" + blockId);
    block.html(parseOutputDiff(text));
}

// Function called in he returned feedback from submission
function createDownloadLink(filename, _){
    // Second parameter is not longer used. However must be kept to steel support previous submissions.
    const attributes = 'class="btn-link" download="' + filename + '"';
    const url = `/course/${getCourseId()}/${getTaskId()}/${filename}`;
    const element = `<a ${attributes} href="${url}" target="_blank">Download</a>`;
    // Write our new downloadable link. On div placeholder
    document.getElementById(filename + '_download_link').innerHTML = element + "<br/><br/>";
}

function parseOutputDiff(diff) {
    let result = [];
    let lines = diff.split('\n');

    // Convention
    result.push('<strong>Legend:</strong> <span class="diff-missing-output">Only in the expected output</span> ' +
      '<span class="diff-additional-output">Only in your output</span> ' +
      '<span class="diff-common">Common</span> ' +
      '<span class="diff-position-control">Context information</span>');
  
    for(let i = 0; i < lines.length; ++i) {
      let line = lines[i];
      let output = null;

      if (line.startsWith("---")) {
        output = '<span class="diff-missing-output">' + line.substring(4) + '</span>';
      } else if (line.startsWith("+++")) {
        output = '<span class="diff-additional-output">' + line.substring(4) + '</span>';
      } else if (line.startsWith("@@")) {
        output = '<span class="diff-position-control">' + line + '</span>';
      } else if (line.startsWith("-")) {
        output = '<span class="diff-missing-output">' + line.substring(1) + '</span>';
      } else if (line.startsWith("+")) {
        output = '<span class="diff-additional-output">' + line.substring(1) + '</span>';
      } else if (line.startsWith(" ")) {
        output = '<span class="diff-common">' + line.substring(1) + '</span>';
      } else if (line.startsWith("...")) {
        output = '<span class="diff-position-control">' + line + '</span>';
      } else if (line === "") {
        // The diff output includes empty lines after position control lines, so we keep them
        // unformatted to avoid misleading the user (they are not actually part of any of the outputs)
        output = line;
      } else {
        throw new Error("Unable to parse diff line: " + line);
      }
      result.push(output);
    }
  
    return result.join("\n");
}
