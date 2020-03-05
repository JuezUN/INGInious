Plotly.d3.json("/api/analytics_consult/", function(err, rows){
   const services_visits = {};
   const dates = [];

   rows.forEach((item, _) => {
      // Object: Service - Date -> number_of_visits
      let date = new Date(item.date);
      date.setHours(0); date.setMinutes(0); date.setSeconds(0); date.setMilliseconds(0);
      
      if( !(item.service in services_visits)){
         services_visits[item.service] = {};
         services_visits[item.service][date.toISOString()] = 0;
      }
      services_visits[item.service][date.toISOString()] += 1;
      dates.push(date.toISOString())

   });

   const data_complete = {};
   for(service in services_visits){
      data_complete[service] = {};
      dates.forEach((item, _) => {
         data_complete[service][item] = 0
      });

      dates.forEach((item, _) => {
         if( item in services_visits[service] )
            data_complete[service][item] += 1;
      })
   }

   const xData = Object.keys(data_complete);
   const yData = Array(xData.length);

   Object.keys(data_complete).forEach((service, index) => {
      let info = [];
      dates.forEach((date, _) => {
         info.push( data_complete[service][date] )
      });
      yData[index] = info;
   });

   const data = [];
   for ( let i = 0; i < xData.length; i++ ) {
      let result = {
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
   }

   const layout = {
      title: 'Plugin Services and Tools Used by the Students',
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
});
