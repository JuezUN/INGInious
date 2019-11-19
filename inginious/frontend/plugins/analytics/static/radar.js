var username = document.getElementById("student_username").value;
    var service = document.getElementById('service').value;
    parameters = [];

    var request = "http://localhost:8080/api/analytics_consult/";
    if(username)
        request += "?"
    if(username)
        parameters.push('username=' + username)

    request += parameters.join('&')

Plotly.d3.json(request, function(err, rows){

  services_visits = {}

  rows.forEach((item, _) => {
    if( item.service in services_visits )
      services_visits[item.service] += 1
    else
      services_visits[item.service] = 1
  });

  services = Object.keys(services_visits)
  visits = services.map((service) => { return services_visits[service]; })

  // Add the first element for visualization
  services.push( services[0] )
  visits.push( visits[0] )

  data = [
    {
      type: 'scatterpolar',
      r: visits,
      theta: services,
      fill: 'toself',
      name: 'Group A'
    }
  ]

  layout = {
    polar: {
      radialaxis: {
        visible: true,
        range: [0, Math.max.apply( this, visits )]
      }
    }
  }

  Plotly.plot("myDiv3", data, layout, {showSendToCloud: true})
})


