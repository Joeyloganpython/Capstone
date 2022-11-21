let buttons =[
  {
    name: "County Level Dashboard",
    filename: "index.html",
  },
  {
    name: "State Level Dashboard",
    filename: "state_level.html",
  },
  {
    name: "Survival Rate Dashboard",
    filename: "survival_rate_wo_naloxone.html"
  },
  {
    name: "Risky Prescription Story",
    filename: "risky_opioid_prescriptions_pa.html"
  }
]

var current_document_name = document.URL.split("/").pop();
let homepage = document.URL.split("/").pop() == "index.html" || document.URL.split("/").pop() == "";

var sidebar = document.createElement('div');
sidebar.className = 'sidebar';

// Add heading to sidebar
var heading = document.createElement('h1');
heading.innerHTML = 'Menu';
sidebar.appendChild(heading);

let list = document.createElement('ul');
list.className = 'nav';

for (let i = 0; i < buttons.length; i++) {
  let line = document.createElement('li');
  let link = document.createElement('a');
  
  if(homepage){
    if(i > 0){
      link.href = "./src/" + buttons[i]['filename'];
    }
    else{
      link.href = "./index.html";
    }
  }
  else{
    if(i == 0){
      link.href = "../" + buttons[i]['filename'];
    }
    else
    {
      link.href = "./" + buttons[i]['filename'];
    }
  }

  if(buttons[i]['filename'] == current_document_name || (i == 0 && homepage)){
    let colored_text = document.createElement("span");
    colored_text.className = "current-page";
    colored_text.innerHTML = buttons[i]['name'];
    link.appendChild(colored_text);
  }
  else{
    link.innerHTML = buttons[i]['name'];
  }
  line.appendChild(link);
  list.appendChild(line);
}
sidebar.appendChild(list);

document.body.appendChild(sidebar);
