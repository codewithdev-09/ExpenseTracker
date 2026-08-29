// ===============================
// GET FORM
// ===============================

const expenseForm = document.getElementById("expenseForm");

// ===============================
// SAVE EXPENSE
// ===============================

expenseForm.addEventListener("submit", function(e){

    e.preventDefault();

    // Get values

    const title = document.getElementById("title").value.trim();
    const category = document.getElementById("category").value;
    const amount = document.getElementById("amount").value;
    const date = document.getElementById("date").value;
    const description = document.getElementById("description").value.trim();

    // Validation

    if(title==="" || amount==="" || date===""){

        alert("Please fill all required fields.");

        return;

    }

    // Create expense object

    const expense={

        id:Date.now(),

        title:title,

        category:category,

        amount:Number(amount),

        date:date,

        description:description

    };

    // Get previous expenses

    let expenses=JSON.parse(localStorage.getItem("expenses")) || [];

    // Add new expense

    expenses.push(expense);

    // Save

    localStorage.setItem("expenses",JSON.stringify(expenses));

    alert("Expense Added Successfully!");

    // Reset Form

    expenseForm.reset();

});