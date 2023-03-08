let buttons =[
  {
    name: "home",
    filename: "index.html",
  },
  {
    name: "Cluster Analysis",
    filename: "cluster.html",
  },
  {
    name: "Classification - Survival",
    filename: "survival_clf.html",
  },
  {
    name: "Classification - Naloxone",
    filename: "naloxone_clf.html"
  },
  {
    name: "Time Series County Level",
    filename: "timeseries.html"
  },
  {
    name: "Linear Regression State Level",
    filename: "lr_state_level.html"
  }
]

function show_tabs(num){
	for (let i = 0; i < buttons.length; i++) {
	  var tabs_cont = document.getElementById("tabs");
	  
	  // Create li
	  var temp_li = document.createElement('li');
	  temp_li.className = 'nav-item';

	  var temp_link = document.createElement('a')
	  
	  // Ensure button is active if current webpage
	  if(num == i){
	  	temp_link.className = 'nav-link active';
	  	temp_link.setAttribute('aria-current', 'page');
	  }
	  else
	  {
	  	temp_link.className = 'nav-link';
	  }

    if(i == 0){
      temp_link.href = "../../"+ buttons[i]['filename'];
    }
    else{
      temp_link.href = "./" + buttons[i]['filename'];
    }
	  temp_link.innerHTML = buttons[i]['name'];
	  temp_li.appendChild(temp_link);
	  tabs_cont.appendChild(temp_li);
	}
}