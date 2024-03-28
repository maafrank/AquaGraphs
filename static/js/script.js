document.addEventListener("DOMContentLoaded", function(event) {
    var seasonal_spec = {{ seasonal_chart_spec | tojson }};
    vegaEmbed('#seasonal-chart', seasonal_spec, { "actions": false }).then(function(result) {
    }).catch(console.error);
});

document.addEventListener("DOMContentLoaded", function(event) {
    var tideInfluenceSpec = {{ tide_influence_chart_spec | tojson }};
    vegaEmbed('#tide-influence-chart', tideInfluenceSpec, { "actions": false }).then(function(result) {
    }).catch(console.error);
});

document.addEventListener("DOMContentLoaded", function(event) {
    var swellDirSpec = {{ swell_direction_chart_spec | tojson }};
    vegaEmbed('#swell-dir-chart', swellDirSpec, { "actions": false }).then(function(result) {
    }).catch(console.error);
});

document.addEventListener("DOMContentLoaded", function(event) {
    var peakPeriodLineSpec = {{ peak_period_line_chart_spec | tojson }};
    vegaEmbed('#peak-period-line-chart', peakPeriodLineSpec, { "actions": false }).then(function(result) {
    }).catch(console.error);
});

document.addEventListener("DOMContentLoaded", function(event) {
    var peakPeriodSpec = {{ peak_period_chart_spec | tojson }};
    vegaEmbed('#peak-period-chart', peakPeriodSpec, { "actions": false }).then(function(result) {
    }).catch(console.error);
});

document.addEventListener("DOMContentLoaded", function(event) {
    var swellPartitionsSpec = {{ swell_partitions_chart_spec | tojson }};
    vegaEmbed('#swell-partitions-chart', swellPartitionsSpec, { "actions": false }).then(function(result) {
    }).catch(console.error);
});

document.addEventListener("DOMContentLoaded", function(event) {
    var swellPartitionsSpec2 = {{ swell_partitions_chart_spec2 | tojson }};
    vegaEmbed('#swell-partitions-chart2', swellPartitionsSpec2, { "actions": false }).then(function(result) {
    }).catch(console.error);
});

document.addEventListener("DOMContentLoaded", function(event) {
    var bigChartSpec1 = {{ big_chart1 | tojson }};
    vegaEmbed('#big-chart1', bigChartSpec1, { "actions": false }).then(function(result) {
    }).catch(console.error);
});

document.addEventListener("DOMContentLoaded", function(event) {
    var smallChartSpec1 = {{ small_chart1 | tojson }};
    vegaEmbed('#small-chart1', smallChartSpec1, { "actions": false }).then(function(result) {
    }).catch(console.error);
});


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
     <h2><strong>lotusSigh_mt: Total significant wave height in meters:</strong></h2>
    <p>In oceanography and marine forecasting, the "significant wave height" is a key statistic describing wave heights in water. It represents the average height of the highest one-third of waves observed over a specific period, providing a reliable estimation of wave conditions for mariners and surfers.</p>
    <p>This metric is crucial for understanding sea conditions, focusing on larger waves that have greater impacts on activities such as surfing, boating, and coastal engineering. The "mt" signifies measurements in meters, adhering to international standards for scientific and navigational purposes.</p>
    <p>Essentially, it indicates the average height of the highest one-third of waves at a location, measured in meters, vital for predicting surfing and sea conditions.</p>
  `;
	break;
    case "tide_ft":
	description = `
     <h2><strong>tide_ft: Tide level in feet:</strong></h2>
    <p>Represents the tide level, crucial for oceanographic data and surf forecasting, showing the sea level at a specific time and location relative to a standard reference point. Tides, caused by gravitational interactions between Earth, Moon, and Sun, are essential for understanding:</p>
    <ul>
      <li><strong>Surfing and Coastal Activities:</strong> Tides affect wave shapes and quality, critical for selecting the best surf times.</li>
      <li><strong>Marine Navigation:</strong> Tides influence water body depths, vital for safe boat and ship navigation.</li>
      <li><strong>Coastal Management:</strong> Tides play a role in coastal erosion, sediment deposition, and marine life distribution, important for coastal planning and environmental management.</li>
      <li><strong>Fishing:</strong> Tidal levels impact marine life behavior and locations, important for fishing activities.</li>
    </ul>
    <p>The "_ft" indicates measurements in feet, commonly used in the United States for distance and height.</p>
  `;
	break;
    case "lotusMinBWH_ft":
	description = `
     <h2><strong>lotusMinBWH_ft: Minimum breaking wave height at the beach in feet:</strong></h2>
    <p>Defines the lowest height waves start to break, crucial for surfability and beach safety. Influenced by sea floor topography, wave energy, and tide levels, it varies by beach due to local conditions.</p>
    <ul>
      <li><strong>Breaking Wave Height:</strong> Height of a wave as it starts to break, critical for assessing surf conditions.</li>
      <li><strong>Minimum Breaking Wave Height:</strong> Indicates the lowest height waves break, offering insights into potential surfing conditions and safety considerations.</li>
      <li><strong>Measurement in Feet:</strong> Uses the imperial system, common in countries like the United States, providing direct wave height indication.</li>
      <li><strong>At the Beach:</strong> Specifies measurement relevance to particular beach locations, where breaking wave heights can vary significantly.</li>
    </ul>
    <p>This metric helps assess beach conditions for surfing, shorebreak risk, and other recreational or safety considerations.</p>
  `;
	break;
    case "lotusMaxBWH_ft":
	description = `
     <h2><strong>lotusMaxBWH_ft: Maximum breaking wave height at the beach in feet:</strong></h2>
    <p>Denotes the highest height waves are seen to break at specific beach locations, measured in feet. Essential for gauging potential maximum wave conditions, impacting surfing, safety, and coastal management.</p>
    <ul>
      <li><strong>Maximum Breaking Wave Height:</strong> The tallest height waves break, influenced by wind speed, swell direction, and seabed contours.</li>
      <li><strong>Measurement in Feet:</strong> Height measured in feet, a standard unit in the United States, aiding surfers and coastal managers in planning and safety.</li>
      <li><strong>At the Beach:</strong> Measurement specific to beach locations, where wave conditions vary greatly due to local topography and geographical factors.</li>
    </ul>
    <p>"lotusMaxBWH_ft" informs on the upper wave height limit at beaches, offering insights into extreme surfing conditions and coastal infrastructure considerations.</p>
  `;
	break;
    case "lotusSighPartX_mt":
	description = `
    <h2><strong>lotusSighPartX_mt: Significant wave height of swell partition X in meters:</strong></h2>
    <p>Denotes the significant wave height within a specific swell partition, vital for marine forecasting. "LOTUS" is Surfline's model, "Sigh" represents "Significant Height", and "PartX" refers to individual swell systems affecting a location, with "X" as the partition number.</p>
    <ul>
      <li><strong>lotus:</strong> Surfline's forecast model.</li>
      <li><strong>Sigh:</strong> Abbreviation for "Significant Height", indicating the average height of the highest third of waves.</li>
      <li><strong>PartX:</strong> Denotes multiple swell partitions, with "X" specifying the partition number, allowing differentiation between swell systems.</li>
      <li><strong>_mt:</strong> Measurement unit in meters, providing a standardized measure of wave heights.</li>
    </ul>
    <p>This metric is crucial for surfers and maritime operations, offering insights into wave energy and surf quality across different swell sources.</p>
  `;
	break;
    case "lotusTPPartX_sec":
	description = `
    <h2><strong>lotusTPPartX_sec: Peak period of swell partition X in seconds:</strong></h2>
    <p>Key to surf forecasting, this indicates the time interval between successive waves in a swell's most energy-dense part, measured in seconds. The "TP" stands for "Peak Period," and "PartX" for a specific swell partition, with "X" denoting the partition number.</p>
    <ul>
      <li><strong>Shorter Peak Periods (5-8 seconds):</strong> Suggest locally generated wind swells, typically less powerful and choppier.</li>
      <li><strong>Longer Peak Periods (12-20 seconds or more):</strong> Indicate swells from distant storms, characterized by more organized, powerful, and cleaner waves.</li>
    </ul>
    <p>This measurement is crucial for predicting wave size, energy, and surf quality, aiding in identifying optimal surfing conditions.</p>
  `;
	break;
    case "lotusPDirPartX_deg":
	description = `
    <h2><strong>lotusPDirPartX_deg: Compass direction of swell partition X in degrees:</strong></h2>
    <p>Indicates the primary direction from which a swell partition originates, using degrees. "LotusPDir" likely refers to "Lotus Peak Direction," with "PartX" signifying individual swell partitions distinguished by origin, period, or direction.</p>
    <ul>
      <li><strong>_deg:</strong> Direction measured in degrees, adhering to compass conventions (North as 0/360, East as 90, South as 180, West as 270).</li>
    </ul>
    <p>This data is vital for predicting how swells interact with coastlines and underwater features, influencing wave characteristics and surfing conditions.</p>
  `;
	break;
    case "lotusSpreadPartX_deg":
	description = `
    <h2><strong>lotusSpreadPartX_deg: Spread of swell partition X in degrees:</strong></h2>
    <p>Defines the range of directions from which waves in a swell partition are arriving, measured in degrees. A narrow spread indicates waves come from a uniform direction, producing consistent surf conditions. A wide spread suggests a broader range of directions, leading to mixed or chaotic sea states, impacting surf conditions and beach safety.</p>
    <p>For example, a main direction of 270 degrees (west) with a 30-degree spread indicates waves moving primarily west but can vary from 255 (WSW) to 285 degrees (WNW).</p>
  `;
	break;
	// Add more cases if needed
	    }
    descriptionElement.innerHTML = description;
}
