document.addEventListener("DOMContentLoaded", function () {

    // ==================================================
    // GET FLASK DATA
    // ==================================================

    const reportData =
        document.getElementById("reportData");

    if (!reportData) {
        console.error("Report data container not found.");
        return;
    }


    let labels = [];
    let values = [];
    let income = 0;
    let expense = 0;
    let monthLabels = [];
    let monthValues = [];


    try {

        labels =
            JSON.parse(
                reportData.dataset.labels || "[]"
            );

        values =
            JSON.parse(
                reportData.dataset.values || "[]"
            );

        income =
            Number(
                JSON.parse(
                    reportData.dataset.income || "0"
                )
            );

        expense =
            Number(
                JSON.parse(
                    reportData.dataset.expense || "0"
                )
            );

        monthLabels =
            JSON.parse(
                reportData.dataset.monthLabels || "[]"
            );

        monthValues =
            JSON.parse(
                reportData.dataset.monthValues || "[]"
            );

    } catch (error) {

        console.error(
            "Error reading report data:",
            error
        );

    }


    // ==================================================
    // COMMON CHART SETTINGS
    // ==================================================

    Chart.defaults.font.family =
        "Poppins, Arial, sans-serif";

    Chart.defaults.color =
        "#596655";


    // ==================================================
    // EXPENSE CATEGORY DOUGHNUT
    // ==================================================

    const expenseCanvas =
        document.getElementById("expensePieChart");

    const noExpenseCategory =
        document.getElementById("noExpenseCategory");


    if (
        expenseCanvas &&
        labels.length > 0 &&
        values.length > 0
    ) {

        new Chart(expenseCanvas, {

            type:"doughnut",

            data:{

                labels:labels,

                datasets:[{

                    data:values,

                    backgroundColor:[
                        "#A8E600",
                        "#7ED957",
                        "#56C596",
                        "#42BFA5",
                        "#B7E85A",
                        "#8FD694",
                        "#C3F584",
                        "#69C97D"
                    ],

                    borderColor:
                        "rgba(255,255,255,.90)",

                    borderWidth:3,

                    hoverOffset:10

                }]

            },

            options:{

                responsive:true,

                maintainAspectRatio:false,

                cutout:"67%",

                plugins:{

                    legend:{

                        position:"bottom",

                        labels:{

                            usePointStyle:true,

                            pointStyle:"circle",

                            padding:18,

                            font:{
                                size:11,
                                weight:"600"
                            }

                        }

                    },

                    tooltip:{

                        callbacks:{

                            label:function(context){

                                const amount =
                                    Number(context.raw);

                                return (
                                    context.label +
                                    ": ₹" +
                                    amount.toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits:2,
                                            maximumFractionDigits:2
                                        }
                                    )
                                );

                            }

                        }

                    }

                }

            }

        });

    } else {

        if (expenseCanvas) {
            expenseCanvas.style.display = "none";
        }

        if (noExpenseCategory) {
            noExpenseCategory.style.display = "flex";
        }

    }


    // ==================================================
    // INCOME VS EXPENSE BAR CHART
    // ==================================================

    const comparisonCanvas =
        document.getElementById("incomeExpenseChart");


    if (comparisonCanvas) {

        new Chart(comparisonCanvas, {

            type:"bar",

            data:{

                labels:[
                    "Income",
                    "Expense"
                ],

                datasets:[{

                    data:[
                        income,
                        expense
                    ],

                    backgroundColor:[
                        "rgba(126,217,87,.72)",
                        "rgba(255,120,120,.65)"
                    ],

                    borderColor:[
                        "#61B846",
                        "#E26767"
                    ],

                    borderWidth:2,

                    borderRadius:12,

                    maxBarThickness:90

                }]

            },

            options:{

                responsive:true,

                maintainAspectRatio:false,

                scales:{

                    y:{

                        beginAtZero:true,

                        grid:{
                            color:"rgba(80,110,80,.08)"
                        },

                        ticks:{

                            callback:function(value){

                                return "₹" +
                                    Number(value)
                                    .toLocaleString("en-IN");

                            }

                        }

                    },

                    x:{

                        grid:{
                            display:false
                        }

                    }

                },

                plugins:{

                    legend:{
                        display:false
                    },

                    tooltip:{

                        callbacks:{

                            label:function(context){

                                return "₹" +
                                    Number(context.raw)
                                    .toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits:2,
                                            maximumFractionDigits:2
                                        }
                                    );

                            }

                        }

                    }

                }

            }

        });

    }


    // ==================================================
    // MONTHLY EXPENSE TREND
    // ==================================================

    const monthlyCanvas =
        document.getElementById("monthlyExpenseChart");

    const noMonthlyData =
        document.getElementById("noMonthlyData");


    if (
        monthlyCanvas &&
        monthLabels.length > 0 &&
        monthValues.length > 0
    ) {

        new Chart(monthlyCanvas, {

            type:"line",

            data:{

                labels:monthLabels,

                datasets:[{

                    label:"Monthly Expense",

                    data:monthValues,

                    borderColor:"#65B95B",

                    backgroundColor:
                        "rgba(126,217,87,.14)",

                    borderWidth:3,

                    fill:true,

                    tension:.4,

                    pointRadius:4,

                    pointHoverRadius:7,

                    pointBackgroundColor:"#65B95B"

                }]

            },

            options:{

                responsive:true,

                maintainAspectRatio:false,

                interaction:{

                    intersect:false,

                    mode:"index"

                },

                scales:{

                    y:{

                        beginAtZero:true,

                        grid:{
                            color:"rgba(80,110,80,.08)"
                        },

                        ticks:{

                            callback:function(value){

                                return "₹" +
                                    Number(value)
                                    .toLocaleString("en-IN");

                            }

                        }

                    },

                    x:{

                        grid:{
                            display:false
                        }

                    }

                },

                plugins:{

                    legend:{

                        labels:{

                            usePointStyle:true,

                            pointStyle:"circle",

                            font:{
                                weight:"600"
                            }

                        }

                    },

                    tooltip:{

                        callbacks:{

                            label:function(context){

                                return "Expense: ₹" +
                                    Number(context.raw)
                                    .toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits:2,
                                            maximumFractionDigits:2
                                        }
                                    );

                            }

                        }

                    }

                }

            }

        });

    } else {

        if (monthlyCanvas) {
            monthlyCanvas.style.display = "none";
        }

        if (noMonthlyData) {
            noMonthlyData.style.display = "flex";
        }

    }

});