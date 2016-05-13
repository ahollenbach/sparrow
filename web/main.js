var ctx = document.getElementById("worker-chart");
var data = {
    labels: [],
    datasets: [
        {
            label: "Worker Loads",
            backgroundColor: "rgba(255,99,132,0.2)",
            borderColor: "rgba(255,99,132,1)",
            borderWidth: 1,
            hoverBackgroundColor: "rgba(255,99,132,0.4)",
            hoverBorderColor: "rgba(255,99,132,1)",
            data: [],
        }
    ]
};

var barChart = new Chart(ctx, {
    type: 'bar',
    data: data,
    options: {
      scales: {
          xAxes: [{
              scaleLabel: {
                display: true,
                labelString: 'Workers'
              }
          }],
          yAxes: [{
              ticks: {
                  max: 20,
                  min: 0
              },
              scaleLabel: {
                display: true,
                labelString: 'Current load (# of tasks)'
              }
          }]
      }
    }
});

window.setInterval(function(){
  $.get("http://hollabook.student.rit.edu:8901/sparrow/status", function(response) {
    $.each(response, function(worker_name, worker_load) {
      var worker_elem = $("#workers #" + worker_name)
      if (worker_elem.length) {
        worker_elem.children(".worker_load").html(worker_load)
      } else {
        $("#workers").append(
          "<div id='" + worker_name + "'>" +
            "<div class='worker_name'>" + worker_name + "</div>" +
            "<div class='worker_load'>" + worker_load + "</div>" +
          "</div>");

        barChart.data.labels.push(worker_name)
        barChart.data.datasets[0].data.push(worker_load)
      }
    });
    for(var i = 0; i < barChart.data.labels.length; i++) {
      var worker_name = barChart.data.labels[i]
      if (typeof(response[worker_name]) !== 'undefined') {
        barChart.data.datasets[0].data[i] = response[worker_name]
      } else {
        // Mark red or something to denote not up
      }
    }

    barChart.update()
  })
}, 2000);
