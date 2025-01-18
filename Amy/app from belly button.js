// Build the metadata panel
function buildMetadata(sample) {
  d3.json("https://static.bc-edx.com/data/dl-1-2/m14/lms/starter/samples.json").then((data) => {

    // get the metadata field
    let metadata = data.metadata;
    console.log('Metadata: ', metadata); //log the whole metadata array

    // Filter the metadata for the object with the desired sample number
    let result = metadata.filter(meta => meta.id ==sample)[0];
    console.log("Filtered Metadata: ", result);  // Log the filtered metadata 

    // Use d3 to select the panel with id of `#sample-metadata`
    let metadataPanel = d3.select('#sample-metadata');

    // Use `.html("") to clear any existing metadata
    metadataPanel.html('');

    // Inside a loop, use d3 to append new
    // tags for each key-value in the filtered metadata.
    Object.entries(result).forEach(([key, value]) => {
      metadataPanel.append('p').text(`${key}: ${value}`);      
    });
  });
}

// function to build both charts
function buildCharts(sample) {
  d3.json("https://static.bc-edx.com/data/dl-1-2/m14/lms/starter/samples.json").then((data) => {

    // Get the samples field
    let samples = data.samples;

    // Filter the samples for the object with the desired sample number
    let result = samples.filter(sampleObj => sampleObj.id == sample)[0];

    // Get the otu_ids, otu_labels, and sample_values
    let otu_ids = result.otu_ids;
    let otu_labels = result.otu_labels
    let sample_values = result.sample_values

    console.log("OTU IDs: ", otu_ids);        // Log the OTU IDs
    console.log("OTU Labels: ", otu_labels);  // Log the OTU Labels
    console.log("Sample Values: ", sample_values); // Log the Sample Values

    // Build a Bubble Chart
    let bubbleData = [{
      type: 'scatter',
      mode: 'markers',
      x: otu_ids,
      y: sample_values,
      marker: {
        size: sample_values,
        color: otu_ids,
        colorscale: 'Earth'
      },
      text: otu_labels
    }]

    let bubbleLayout = {
      title: 'Bacteria Cultures Per Sample',
      xaxis: {title: "OTU ID"},
      yaxis: {title: 'Number of Bacteria'},
      showlegend: false
    };

    // Render the Bubble Chart
    Plotly.newPlot('bubble', bubbleData, bubbleLayout);


    // For the Bar Chart

    // Sort the data by sample_values in descending order to have the highest sample values first 
    let sortedData = sample_values
      .map((value, index) => {
        return {
          sample_value: value,
          otu_id: otu_ids[index],
          otu_label: otu_labels[index]
        };
      })
      .sort((a, b) => b.sample_value - a.sample_value);

      console.log("Sorted Data: ", sortedData);  // Log the sorted data before slicing
      
      // Slice the first 10 objects for plotting
      let top10Data = sortedData.slice(0, 10);
      console.log("Top 10 Data: ", top10Data);  // Log the top 10 data after slicing

      // Reverse the array to accomodate Plotly's default behavior
      top10Data.reverse();
      console.log("Reversed Top 10 Data: ", top10Data);  // Log the reversed data

      // Map the otu_ids to a list of strings for the yticks
      let yticks = top10Data.map(object => `OTU ${object.otu_id}`);

      let trace1 = {
        x: top10Data.map(object => object.sample_value), 
        y: yticks, // using the mapped OTU IDs 
        text: top10Data.map(object => object.otu_label), // Labels for the hover text
        type: "bar", 
        orientation: "h" 
      };
      
      // Layout for the Bar Chart
      let layout = {
        title: "Top 10 Bacteria Cultures Found", 
        xaxis: { title: "Number of Bacteria" }, 
        yaxis: { title: " " }, 
        margin: { l: 100, r: 100, t: 100, b: 100 } 
      };

    // Render the Bar Chart
    Plotly.newPlot("bar", [trace1], layout);

  });
}

// Function to run on page load
function init() {
  d3.json("https://static.bc-edx.com/data/dl-1-2/m14/lms/starter/samples.json").then((data) => {

    // Get the names field
    let sampleNames = data.names;
    console.log("Sample Names: ", sampleNames);  // Log the list of sample names

    // Use d3 to select the dropdown with id of `#selDataset`
    let dropdown = d3.select('#selDataset')


    // Use the list of sample names to populate the select options
    sampleNames.forEach(function(name) {
      dropdown.append('option').text(name).property('value', name);
    })

    // Get the first sample from the list
    let firstSample =sampleNames[0];
    console.log("First Sample: ", firstSample);  // Log the first sample

    // Build charts and metadata panel with the first sample
    buildCharts(firstSample);
    buildMetadata(firstSample);

  });
}

// Function for event listener
function optionChanged(newSample) {
  console.log("New Sample Selected: ", newSample);  // Log the newly selected sample
  // Build charts and metadata panel each time a new sample is selected
  buildCharts(newSample);
  buildMetadata(newSample);
}

// Initialize the dashboard
init();
