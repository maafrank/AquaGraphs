document.addEventListener("DOMContentLoaded", function(event) {
    const scroller = scrollama();
    
    function handleStepEnter(response) {
        response.element.classList.add('is-active');
    }
    
    function handleStepExit(response) {
        response.element.classList.remove('is-active');
    }
    
    scroller.setup({
        step: '.step',
        offset: 0.5,
        enter: handleStepEnter,
        exit: handleStepExit
    }).onStepEnter(handleStepEnter)
        .onStepExit(handleStepExit);
    
    // Make the first step visible
    document.querySelector('.step').classList.add('is-active');
    
    window.addEventListener('resize', scroller.resize);
});



document.addEventListener("DOMContentLoaded", function(event) {
    fetchChartDataAndEmbed('/get-seasonal-spec', '#seasonal-chart');
    fetchChartDataAndEmbed('/get-tide-influence-spec', '#tide-influence-chart');
    fetchChartDataAndEmbed('/get-swell-direction-spec', '#swell-dir-chart');
    fetchChartDataAndEmbed('/get-peak-period-line-spec', '#peak-period-line-chart');
    fetchChartDataAndEmbed('/get-peak-period-spec', '#peak-period-chart');
    fetchChartDataAndEmbed('/get-swell-partitions-spec', '#swell-partitions-chart');
    fetchChartDataAndEmbed('/get-swell-partitions-spec2', '#swell-partitions-chart2');
    fetchChartDataAndEmbed('/get-big-chart1', '#big-chart1');
    fetchChartDataAndEmbed('/get-small-chart1', '#small-chart1');
	fetchChartDataAndEmbed('/partition_height_period_update', '#partition_height_period');
});

function fetchChartDataAndEmbed(apiEndpoint, embedContainerId) {
    fetch(apiEndpoint)
        .then(response => response.json())
        .then(chartSpec => {
            vegaEmbed(embedContainerId, chartSpec, { "actions": false })
                .then(function(result) {
                    // Chart successfully embedded
                    console.log(`Chart embedded: ${embedContainerId}`);
                })
                .catch(console.error);
        })
        .catch(error => console.error('Error fetching chart data:', error));
}


// Function to load and update chart data
function loadChartData(chartId) {	  
    const variable = document.getElementById(`variable${chartId}`).value;
    const aggregation = document.getElementById(`aggregation${chartId}`).value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    updateDescription(chartId, variable);
    
    const dateQuery = `&startDate=${startDate}&endDate=${endDate}`;
    fetch(`/update_chart?variable=${variable}&aggregation=${aggregation}${dateQuery}`)
	.then(response => response.json())
	.then(chartSpec => {
	    vegaEmbed(`#chart${chartId}`, chartSpec);
	})
	.catch(error => console.error('Error loading chart:', error));
}

function updateChart() {
    loadChartData('1');
}

// Call updateAllCharts initially to load all charts with default or initial dates
updateChart();

function updateDescription(chartId, variable) {
    const descriptionElement = document.getElementById(`chart${chartId}Description`);
    let description = "Select a variable to see its description."; // Default description
    
    // Update description based on the variable
    switch (variable) {
    case "lotusSigh_mt":
	description = `
     <h2><strong>Wave Height (mt): Average High Wave Height in Meters</strong></h2>
<p>"Significant wave height" is the term used to describe the average of the tallest one-third of waves in the sea, which gives sailors and surfers a good idea of what to expect out on the water. It's measured in meters, following the global standard, and helps predict the conditions for various ocean activities.</p>
  `;
	break;
    case "tide_ft":
	description = `
     <h2><strong>Tide (ft): Tide Height in Feet</strong></h2>
<p>This measures how high the tide is, important for anyone who needs to know sea levels, from surfers picking the best waves to sailors ensuring safe passage. Tides affect not just water depth but also the health of coastlines and marine habitats, playing a big part in activities like fishing. The "ft" shows that the height is in feet, which is the standard in the U.S. for such measurements.</p>
  `;
	break;
    case "lotusMinBWH_ft":
	description = `
     <h2><strong>Minimum Breaking Wave Height (ft): Smallest Surfable Wave Height in Feet</strong></h2>
<p>Measures the shortest height where waves begin to break, which is key for surfing and beach safety. This height changes with the ocean's floor shape and the tides, and it's different for each beach. Knowing this figure helps surfers understand the smallest waves they can surf and helps everyone stay safe on the shore. It's measured in feet, the usual unit for the U.S.</p>
  `;
	break;
    case "lotusMaxBWH_ft":
	description = `
     <h2><strong>Maximum Breaking Wave Height (ft): Tallest Wave Height at the Beach in Feet</strong></h2>
<p>Indicates the tallest waves that can break at a beach, a key factor for surfers looking for big waves and for maintaining safety along the shore. Factors like wind, swell direction, and the shape of the sea floor affect this height. Measured in feet for consistency within the U.S., this metric helps with beach safety plans and managing coastal areas.</p>
  `;
	break;
    case "lotusSighPartX_mt":
	description = `
    <h2><strong>Significant Wave Height (mt): Height of Wave Group X in Meters</strong></h2>
<p>Measures the height of a certain group of waves, part of Surfline's LOTUS model, essential for predicting sea conditions. "Sigh" means it's the average of the tallest waves in the group, and "PartX" identifies which group of waves, or swell system, we're looking at. Measured in meters, it helps surfers and those at sea understand what size of waves to expect from different sources.</p>
  `;
	break;
    case "lotusTPPartX_sec":
	description = `
    <h2><strong>Peak Period (sec): Time Between Waves for Swell Group X in Seconds</strong></h2>
<p>Essential for understanding waves, this figure tells us how many seconds pass between waves in the strongest part of a swell. "TP" means "Peak Period," and "PartX" specifies which group of waves we're measuring, with "X" as its identifier.</p>
<p>Short peak periods mean the waves are smaller and choppier, often from local winds. Long peak periods point to big, smooth waves that started from far-off storms. Surfers and ocean forecasters use this to predict the best waves for surfing.</p>
  `;
	break;
    case "lotusPDirPartX_deg":
	description = `
    <h2><strong>Swell Direction (deg): Swell Direction for Wave Group X</strong></h2>
<p>Shows where a group of waves is coming from, measured in compass degrees. "LotusPDir" suggests it's the main direction for the wave group labeled "X." </p>
<p>The direction is noted in degrees, with 0/360 for North, 90 for East, 180 for South, and 270 for West. Knowing this helps forecast how waves will approach the shore, which is key for surfers and coastal planning.</p>
  `;
	break;
    case "lotusSpreadPartX_deg":
	description = `
    <h2><strong>Swell Spread (deg): Wave Direction Range for Group X</strong></h2>
<p>Shows the variety of directions that waves from a particular group are coming from, in degrees. A smaller range means more uniform waves good for surfing, while a larger range could mean unpredictable conditions. For instance, if waves are mostly coming from the west (270 degrees), a 30-degree spread would mean they could be shifting slightly southwest or northwest.</p>
  `;
	break;
	// Add more cases if needed
	    }
    descriptionElement.innerHTML = description;
}

//Added by Millie:
// Function to load and update chart data
function loadChartData2(chartId) {	  
    const variable = document.getElementById(`variable${chartId}`).value;
    const aggregation = document.getElementById(`aggregation${chartId}`).value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    updateDescription(chartId, variable);
    
    const dateQuery = `&startDate=${startDate}&endDate=${endDate}`;
    fetch(`/update_chart?variable=${variable}&aggregation=${aggregation}${dateQuery}`)
	.then(response => response.json())
	.then(chartSpec => {
	    vegaEmbed(`#chart${chartId}`, chartSpec);
	})
	.catch(error => console.error('Error loading chart:', error));
}

function updateChart() {
    loadChartData('1');
}
// Function to load and update partition_height_period
function load_partition_height_period() {
    const partition_height_period_unit = document.getElementById(`partition_height_period_unit`).value;
	    fetch(`/partition_height_period_update?partition_height_period_unit=${partition_height_period_unit}`)
		.then(response => response.json())
		.then(chartSpec => {
		    vegaEmbed(`#partition_height_period`, chartSpec);
		})
		.catch(error => console.error('Error loading chart:', error));
    
}
