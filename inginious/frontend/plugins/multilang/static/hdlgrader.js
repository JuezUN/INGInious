function updateWaveDromBlock(blockId) {
    let block = $("#" + blockId);
    let htmlbeg = block.html();
    block.html(parseOutputDiff(htmlbeg)+parseHDL(htmlbeg));
}

function parseHDL(diff){
  let lines = diff.split('\\n');
  let inputsG = {};
  let outputsG = {};
  let inputsC = {};
  let outputsC = {};

  let noBinary = {};
  let dataG = {};
  let dataC = {};

  let result = [];
  let lastTimeGood = 0;
  let lastTimeBad = 0;
  result.push('<script src="http://wavedrom.com/skins/default.js" type="text/javascript"></script>');
  result.push('<script src="http://wavedrom.com/wavedrom.min.js" type="text/javascript"></script>');
  result.push('<script type="WaveDrom">');

  result.push("{signal: [");
  for(let i = 0; i < lines.length; ++i) {
      let line = lines[i];
      let info = line.replace(/ /g,"").split(",");
      let output = null;
      let time = parseInt(info[1]);


      if (line.startsWith("---")) {
        output = '<span class="diff-missing-output">' + line.substring(4) + '</span>';
      } else if (line.startsWith("+++")) {
        output = '<span class="diff-additional-output">' + line.substring(4) + '</span>';
      } else if (line.startsWith("@@")) {
        output = '<span class="diff-position-control">' + line + '</span>';
      } else if (line.startsWith("-")) {
        let is_input = false;
        let is_output = false;
        if(info.length > 2){
            let j = 2;
            while(j < info.length) {
                if(info[j] === "INPUTS"){
                  is_input = true;
                  is_output = false;
                }else if(info[j] === "OUTPUTS"){
                  is_input = false;
                  is_output = true;
                }else{
                  let signal = info[j];
                  let value = info[j+1];
                  if (is_input){
                    if (time == 0){
                        if(signal.includes("[")) {
                            noBinary[signal] = 1;
                            dataG[signal] = [];
                            inputsG[signal] = "2";
                            dataG[signal].push("'"+value+"'");
                        }else{
                            inputsG[signal] = value;
                        }
                    }else{
                      if (signal in noBinary){
                        if (dataG[signal].slice(-1) == "'"+value+"'"){
                          inputsG[signal] += ".".repeat(time - lastTimeGood);
                        }else{
                          inputsG[signal] += ".".repeat(time - lastTimeGood-1) + "2";
                          dataG[signal].push("'"+value+"'");
                        }
                      }else{
                        if (inputsG[signal].replace(/\./g,"").slice(-1) === value){
                          inputsG[signal] += ".".repeat(time - lastTimeGood);
                        }else{
                          inputsG[signal] += ".".repeat(time - lastTimeGood-1) + value;
                        }
                      }
                    }
                    j++;
                  }else if(is_output){
                    if (time == 0){
                      if(signal.includes("[")) {
                            noBinary[signal] = 1;
                            dataG[signal] = [];
                            outputsG[signal] = "2";
                            dataG[signal].push("'"+value+"'");
                      }else{
                            outputsG[signal] = value;
                      }
                    }else{
                      if (signal in noBinary){
                        if (dataG[signal].slice(-1) == "'"+value+"'"){
                          outputsG[signal] += ".".repeat(time - lastTimeGood);
                        }else{
                          outputsG[signal] += ".".repeat(time - lastTimeGood-1) + "2";
                          dataG[signal].push("'"+value+"'");
                        }
                      }else{
                        if (outputsG[signal].replace(/\./g,"").slice(-1) === value){
                          outputsG[signal] += ".".repeat(time - lastTimeGood);
                        }else{
                          outputsG[signal] += ".".repeat(time - lastTimeGood-1) + value;
                        }
                      }
                    }
                    j++;
                  }
                }
                j++;
            }

            lastTimeGood = time;
        }

        output = '<span class="diff-missing-output">' + line.substring(1) + '</span>';
      } else if (line.startsWith("+")) {
        let is_input = false;
        let is_output = false;
        if(info.length > 2){
            let j = 2;
            while(j < info.length) {
                if(info[j] === "INPUTS"){
                  is_input = true;
                  is_output = false;
                }else if(info[j] === "OUTPUTS"){
                  is_input = false;
                  is_output = true;
                }else{
                  let signal = info[j];
                  let value = info[j+1];
                  if (is_input){
                    if (time == 0){
                        if(signal.includes("[")) {
                            noBinary[signal] = 1;
                            dataC[signal] = [];
                            inputsC[signal] = "2";
                            dataC[signal].push("'"+value+"'");
                        }else{
                            inputsC[signal] = value;
                        }
                    }else{
                      if (signal in noBinary){
                        if (dataC[signal].slice(-1) == "'"+value+"'"){
                          inputsC[signal] += ".".repeat(time - lastTimeBad);
                        }else{
                          inputsC[signal] += ".".repeat(time - lastTimeBad-1) + "2";
                          dataC[signal].push("'"+value+"'");
                        }
                      }else{
                        if (inputsC[signal].replace(/\./g,"").slice(-1) === value){
                          inputsC[signal] += ".".repeat(time - lastTimeBad);
                        }else{
                          inputsC[signal] += ".".repeat(time - lastTimeBad-1) + value;
                        }
                      }
                    }
                    j++;
                  }else if(is_output){
                    if (time == 0){
                      if(signal.includes("[")) {
                            noBinary[signal] = 1;
                            dataC[signal] = [];
                            outputsC[signal] = "2";
                            dataC[signal].push("'"+value+"'");
                      }else{
                            outputsC[signal] = value;
                      }
                    }else{
                      if (signal in noBinary){
                        if (dataC[signal].slice(-1) == "'"+value+"'"){
                          outputsC[signal] += ".".repeat(time - lastTimeBad);
                        }else{
                          outputsC[signal] += ".".repeat(time - lastTimeBad-1) + "2";
                          dataC[signal].push("'"+value+"'");
                        }
                      }else{
                        if (outputsC[signal].replace(/\./g,"").slice(-1) === value){
                          outputsC[signal] += ".".repeat(time - lastTimeBad);
                        }else{
                          outputsC[signal] += ".".repeat(time - lastTimeBad-1) + value;
                        }
                      }
                    }
                    j++;
                  }
                }
                j++;
            }
            lastTimeBad = time;
        }

        output = '<span class="diff-additional-output">' + line.substring(1) + '</span>';
      } else if (line.startsWith(" ")) {
        let is_input = false;
        let is_output = false;
        if(info.length > 2){
            let j = 2;
            while(j < info.length) {
                if(info[j] === "INPUTS"){
                  is_input = true;
                  is_output = false;
                }else if(info[j] === "OUTPUTS"){
                  is_input = false;
                  is_output = true;
                }else{
                  let signal = info[j];
                  let value = info[j+1];
                  if (is_input){
                    if (time == 0){
                        if(signal.includes("[")) {
                            noBinary[signal] = 1;
                            dataC[signal] = [];
                            inputsC[signal] = "2";
                            dataC[signal].push("'"+value+"'");

                            dataG[signal] = [];
                            inputsG[signal] = "2";
                            dataG[signal].push("'"+value+"'");
                        }else{
                            inputsC[signal] = value;
                            inputsG[signal] = value;
                        }
                    }else{
                      if (signal in noBinary){
                        if (dataG[signal].slice(-1) == "'"+value+"'"){
                          inputsG[signal] += ".".repeat(time - lastTimeGood);
                        }else{
                          inputsG[signal] += ".".repeat(time - lastTimeGood-1) + "2";
                          dataG[signal].push("'"+value+"'");
                        }

                        if (dataC[signal].slice(-1) == "'"+value+"'"){
                          inputsC[signal] += ".".repeat(time - lastTimeBad);
                        }else{
                          inputsC[signal] += ".".repeat(time - lastTimeBad-1) + "2";
                          dataC[signal].push("'"+value+"'");
                        }
                      }else{
                        if (inputsG[signal].replace(/\./g,"").slice(-1) === value){
                          inputsG[signal] += ".".repeat(time - lastTimeGood);
                        }else{
                          inputsG[signal] += ".".repeat(time - lastTimeGood-1) + value;
                        }
                        if (inputsC[signal].replace(/\./g,"").slice(-1) === value){
                          inputsC[signal] += ".".repeat(time - lastTimeBad);
                        }else{
                          inputsC[signal] += ".".repeat(time - lastTimeBad-1) + value;
                        }
                      }
                    }
                    j++;
                  }else if(is_output){
                    if (time == 0){
                      if(signal.includes("[")) {
                            noBinary[signal] = 1;
                            dataC[signal] = [];
                            outputsC[signal] = "2";
                            dataC[signal].push("'"+value+"'");

                            dataG[signal] = [];
                            outputsG[signal] = "2";
                            dataG[signal].push("'"+value+"'");
                      }else{
                            outputsC[signal] = value;
                            outputsG[signal] = value;
                      }
                    }else{
                      if (signal in noBinary){
                        if (dataC[signal].slice(-1) == "'"+value+"'"){
                          outputsC[signal] += ".".repeat(time - lastTimeBad);
                        }else{
                          outputsC[signal] += ".".repeat(time - lastTimeBad-1) + "2";
                          dataC[signal].push("'"+value+"'");
                        }
                        if (dataG[signal].slice(-1) == "'"+value+"'"){
                          outputsG[signal] += ".".repeat(time - lastTimeGood);
                        }else{
                          outputsG[signal] += ".".repeat(time - lastTimeGood-1) + "2";
                          dataG[signal].push("'"+value+"'");
                        }
                      }else{
                        if (outputsG[signal].replace(/\./g,"").slice(-1) === value){
                          outputsG[signal] += ".".repeat(time - lastTimeGood);
                        }else{
                          outputsG[signal] += ".".repeat(time - lastTimeGood-1) + value;
                        }
                        if (outputsC[signal].replace(/\./g,"").slice(-1) === value){
                          outputsC[signal] += ".".repeat(time - lastTimeBad);
                        }else{
                          outputsC[signal] += ".".repeat(time - lastTimeBad-1) + value;
                        }
                      }
                    }
                    j++;
                  }
                }
                j++;
            }
            lastTimeGood = time;
            lastTimeBad = time;
        }
        //output = '<span class="diff-common">' + line.substring(1) + '</span>';
      } else if (line.startsWith("...")) {
        output = '<span class="diff-position-control">' + line + '</span>';
      } else if (line === "") {
        // The diff output includes empty lines after position control lines, so we keep them
        // unformatted to avoid misleading the user (they are not actually part of any of the outputs)
        output = line;
      }

      //result.push(output);
  }
  result.push('{name:"Inputs:"},');
  let start = 65; // ASCII for 'A'
  for(var signal in inputsC){
    if (signal in noBinary){
        if (inputsC[signal] === inputsG[signal] && dataC[signal] === dataG[signal] ){
            result.push('{name:"'+signal+'", wave: "'+inputsG[signal]+'", data:['+dataG[signal]+']},');
        }else{
            dataDiff = parseDiffWaveDromBus(inputsC[signal], inputsG[signal], dataC[signal], dataG[signal]);
            result.push('{name:"'+signal+'", '+dataDiff+'},');
            result.push('{name:"'+signal+'*", wave: "'+inputsG[signal]+'", data:['+dataG[signal]+']},');
        }
    }else{
        if ( inputsC[signal] === inputsG[signal]){
            result.push('{name:"'+signal+'", wave: "'+inputsC[signal]+'"},');
        }else{
            nodes = parseDiffWaveDrom(inputsC[signal], inputsG[signal], start);
            result.push('{name:"'+signal+'", wave: "'+inputsC[signal]+'", node:"'+nodes+'"},');
            result.push('{name:"'+signal+'*", wave: "'+inputsG[signal]+'"},');
            start += (nodes.length - (nodes.match(/\./g) || []).length);
        }
    }
  }
  result.push('{name:"Outputs:"},');
  for(var signal in outputsC){
    if (signal in noBinary){
        if (outputsC[signal] === outputsG[signal] && JSON.stringify(dataC[signal]) == JSON.stringify(dataG[signal])  ){
            result.push('{name:"'+signal+'", wave: "'+outputsG[signal]+'", data:['+dataG[signal]+']},');
        }else{
            dataDiff = parseDiffWaveDromBus(outputsC[signal], outputsG[signal], dataC[signal], dataG[signal]);
            result.push('{name:"'+signal+'", '+dataDiff+'},');
            result.push('{name:"'+signal+'*", wave: "'+outputsG[signal]+'", data:['+dataG[signal]+']},');
        }
    }else{
        if ( outputsC[signal] === outputsG[signal]){
            result.push('{name:"'+signal+'", wave: "'+outputsG[signal]+'"},');
        }else{
            nodes = parseDiffWaveDrom(outputsC[signal], outputsG[signal], start);
            result.push('{name:"'+signal+'", wave: "'+outputsC[signal]+'", node:"'+nodes+'"},');
            result.push('{name:"'+signal+'*", wave: "'+outputsG[signal]+'"},');
            start += (nodes.length - (nodes.match(/\./g) || []).length);
        }
    }
  }
  result.push("]");

  if (start != 65){
    result.push(",\"edge\":[");
    edges = []
    for(let j = 65; j<start;j+=2)
        edges.push("'"+String.fromCharCode(j)+"|-|"+String.fromCharCode(j+1)+" diff'")
    result.push(edges.join(", "));
    result.push("]");
  }
  result.push("}");
  result.push('</script>');
  result.push('<script type="text/javascript">function loadWaveDrom(){ var x = document.getElementById("loadButtonWD"); WaveDrom.ProcessAll(); x.style.display = "none";}</script>');
  result.push('<button id="loadButtonWD" onclick="loadWaveDrom()">Load</button> ');

  //return result;
  return result.join("\n");
}

function parseDiffWaveDrom(code, golden, start){
   let node = "";
   let lastC = "";
   let lastG = "";
   let begin = false;
   for (let i=0; i < code.length;i++){
     if (code[i] !== ".") lastC = code[i];
     if (golden[i] !== ".") lastG = golden[i];
     if(lastC !== lastG){
       if (begin){
            node += ".";

       }else{
         node += String.fromCharCode(start);
         start+=1;
         begin = true;
       }
     }else{
       if (begin){
         node += String.fromCharCode(start);
         start+=1;
         begin = false;
       }else{
         node += ".";
       }

     }
   }
   if (begin) node += String.fromCharCode(start);
   return node;

}

function parseDiffWaveDromBus(wcode, wgolden, dcode, dgolden){
/*
{name:"tot[1:0]C", wave: "2..2.....2...........2.....2........", data:['x','0','1','2','1']},
{name:"tot[1:0]G", wave: "2..2..2.....2..2..2.....2..2........", data:['x','0','1','2','1','2','3','2']},
*/
    //wave: "'+outputsG[signal]+'", data:['+dataG[signal]+']
    let wave = "";
    let ndata = [];
    let lastC = "";
    let lastG = "";
    let beginOK = false;
    let beginBad = false;
    let icode = 0;
    let igolden = 0;
    for (let i=0; i < wcode.length;i++){
      if (wcode[i] !== ".") {
        lastC = dcode[icode];
        icode++;
      }
      if (wgolden[i] !== "."){
        lastG = dgolden[igolden];
        igolden++;
      }
      if(lastC != lastG){
        beginOK = false;
        if(lastC != ndata.slice(-1)) beginBad = false;
        if(beginBad){
          wave += '.';
        }else{
          beginBad = true;
          wave += '9';
          ndata.push(lastC);
        }
      }else{
        beginBad = false;
        if(lastC != ndata.slice(-1)) beginOK = false;
        if(beginOK){
          wave += '.';
        }else{
          beginOK = true;
          wave += '2';
          ndata.push(lastC);
        }

      }
    }
    //wave: "'+outputsG[signal]+'", data:['+dataG[signal]+']
    return 'wave: "'+wave+'", data:['+ndata+']';
}

