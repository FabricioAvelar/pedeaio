const pfTab = document.getElementById("pf-tab");
const pjTab = document.getElementById("pj-tab");
const pfForm = document.getElementById("pf-form");
const pjForm = document.getElementById("pj-form");

pfTab.onclick = () => {
    pfTab.classList.add("active");
    pjTab.classList.remove("active");
    pfForm.style.display = "block";
    pjForm.style.display = "none";
}

pjTab.onclick = () => {
    pjTab.classList.add("active");
    pfTab.classList.remove("active");
    pfForm.style.display = "none";
    pjForm.style.display = "block";
}