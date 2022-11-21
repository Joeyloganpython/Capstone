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

console.log(document.URL);
console.log(document.URL.split("/").pop() + " test");
console.log(document.URL.split("/").pop() == "index.html");

var current_document_name = document.URL.split("/").pop();
let homepage = document.URL.split("/").pop() == "index.html";

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
  line.appendChild(link);
  if(homepage){
    if(i > 0){
      link.href = "./src/" + buttons[i]['filename'];
    }
    else{
      link.href = "#";
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
  console.log(i , buttons[i]['filename'] == current_document_name);
  if(buttons[i]['filename'] == current_document_name){
    let colored_text = document.createElement("span");
    colored_text.className = "current-page";
    colored_text.innerHTML = buttons[i]['name'];
    link.appendChild(colored_text);
  }
  else{
    link.innerHTML = buttons[i]['name'];
  }

  list.appendChild(line);
}
sidebar.appendChild(list);

document.body.appendChild(sidebar);
