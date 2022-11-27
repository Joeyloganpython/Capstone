
function show_dashboard(link, small = false){

	// Create viz-container
	var viz_content = document.createElement('div');
	viz_content.className = 'viz-cont';

	// Another container
	var viz = document.createElement('div');
	viz.className = 'viz';
	if(small){
		viz.className = 'viz smallviz';
	}
	
	// That's the actual viz
	var tableau_viz = document.createElement('tableau-viz');
	tableau_viz.id = "tableauViz";
	tableau_viz.src = link;

	// Append all to document 
	viz.appendChild(tableau_viz);
	viz_content.appendChild(viz);
	document.body.appendChild(viz_content);
}