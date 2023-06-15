function plot(x, y, z) {
    var data = [{
               type: 'surface',
               x: x,
               y: y,
               z: z,
            }];
      
    var layout = {
      title: 'Multivariate gaussian distribution',
      autosize: false,
      width: 500,
      height: 500,
      margin: {
        l: 65,
        r: 50,
        b: 65,
        t: 90,
      }
    };
    Plotly.newPlot('plot-box', data, layout);
};
