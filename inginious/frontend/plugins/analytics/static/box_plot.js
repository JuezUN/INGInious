Plotly.d3.json("http://localhost:8080/api/analytics_consult/?service_type=student", function(err, rows){
   services_visits = {}

   dates = []

   rows.forEach((item, _) => {
      // Object: Service - Date -> number_of_visits
      let date = new Date(item.date);
      date.setHours(0); date.setMinutes(0); date.setSeconds(0); date.setMilliseconds(0);
      
      if( !(item.service in services_visits)){
         services_visits[item.service] = {}
         services_visits[item.service][date.toISOString()] = 0
      }
      services_visits[item.service][date.toISOString()] += 1
      dates.push(date.toISOString())

   })


   data_complete = {}
   for(service in services_visits){
      data_complete[service] = {}
      dates.forEach((item, _) => {
         data_complete[service][item] = 0
      })

      dates.forEach((item, _) => {
         if( item in services_visits[service] )
            data_complete[service][item] += 1;
      })
   }


   xData = Object.keys(data_complete);
   yData = Array(xData.length);

   console.log(data_complete)
   console.log(xData)

   Object.keys(data_complete).forEach((service, index) => {
      let info = []
      console.log(data_complete)
      dates.forEach((date, _) => {
         info.push( data_complete[service][date] )
      });
      yData[index] = info;
   })

   data = []
   console.log(yData);
   for ( var i = 0; i < xData.length; i++ ) {
      var result = {
        type: 'box',
        y: yData[i],
        name: xData[i],
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
      data.push(result);
   };

   layout = {
      title: 'Points Scored by the Top 9 Scoring NBA Players in 2012',
      yaxis: {
          autorange: true,
          showgrid: true,
          zeroline: true,
          dtick: 5,
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

  console.log(data);
  Plotly.newPlot('myDiv2', data, layout, {showSendToCloud: true});

});

  
/*



var xData = ['Carmelo<br>Anthony', 'Dwyane<br>Wade',
      'Deron<br>Williams', 'Brook<br>Lopez',
      'Damian<br>Lillard', 'David<br>West',
      'Blake<br>Griffin', 'David<br>Lee',
      'Demar<br>Derozan'];
function getrandom(num , mul) 
{
   var value = [ ]	
	for(i=0;i<=num;i++)
   {
	 rand=Math.random() * mul;
    value.push(rand);
	}
	return value
}
var yData = [
   getrandom(30 ,10),
	getrandom(30, 20),
   getrandom(30, 25),
   getrandom(30, 40),
	getrandom(30, 45),
   getrandom(30, 30),
   getrandom(30, 20),
   getrandom(30, 15),
   getrandom(30, 43)
];

var colors = ['rgba(93, 164, 214, 0.5)', 'rgba(255, 144, 14, 0.5)', 'rgba(44, 160, 101, 0.5)', 'rgba(255, 65, 54, 0.5)', 'rgba(207, 114, 255, 0.5)', 'rgba(127, 96, 0, 0.5)', 'rgba(255, 140, 184, 0.5)', 'rgba(79, 90, 117, 0.5)', 'rgba(222, 223, 0, 0.5)'];

var data = [];
console.log(xData);
console.log(yData);

for ( var i = 0; i < xData.length; i ++ ) {
  var result = {
    type: 'box',
    y: yData[i],
    name: xData[i],
    boxpoints: 'all',
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
  data.push(result);
};

console.log(data); 

layout = {
    title: 'Points Scored by the Top 9 Scoring NBA Players in 2012',
    yaxis: {
        autorange: true,
        showgrid: true,
        zeroline: true,
        dtick: 5,
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

Plotly.newPlot('myDiv2', data, layout, {showSendToCloud: true});

*/