// Cite Code: W3Schools
// https://www.w3schools.com/howto/howto_js_collapse_sidebar.asp 

function openNav() {
  document.getElementById("menu").style.height = "100%";
  document.getElementById("menu").style.overflowY = "scroll";
  document.getElementById("open").style.display = "none";
  document.getElementById("close").style.display = "block";
  
}

function closeNav() {
  document.getElementById("menu").style.height = "100px";
  document.getElementById("menu").style.overflowY = "hidden";
  document.getElementById("close").style.display = "none";
  document.getElementById("open").style.display = "block";

}