// =============================
// Expense History Search & Filter
// =============================

const searchInput = document.getElementById("searchInput");
const categoryFilter = document.getElementById("categoryFilter");
const table = document.getElementById("expenseTable");

function filterTable() {

    const searchText = searchInput.value.toLowerCase();
    const category = categoryFilter.value.toLowerCase();

    const rows = table.getElementsByTagName("tbody")[0].getElementsByTagName("tr");

    for (let row of rows) {

        const title = row.cells[1].innerText.toLowerCase();
        const cat = row.cells[2].innerText.toLowerCase();

        const titleMatch = title.includes(searchText);
        const categoryMatch = category === "" || cat === category;

        if (titleMatch && categoryMatch) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }

    }

}

searchInput.addEventListener("keyup", filterTable);
categoryFilter.addEventListener("change", filterTable);