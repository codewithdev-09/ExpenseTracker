// ======================================================
// EXPENSE TRACKER DASHBOARD
// ======================================================


document.addEventListener("DOMContentLoaded", function () {


    // ==================================================
    // GET CHART ELEMENT
    // ==================================================

    const ctx = document.getElementById("myChart");

    const noDataMessage =
        document.getElementById("noChartData");


    // ==================================================
// GET REAL DATA FROM FLASK
// ==================================================

const chartData =
    document.getElementById("chartData");

let labels = [];
let values = [];

if (chartData) {

    try {

        labels = JSON.parse(
            chartData.dataset.labels || "[]"
        );

        values = JSON.parse(
            chartData.dataset.values || "[]"
        );

    } catch (error) {

        console.error(
            "Error loading chart data:",
            error
        );

        labels = [];
        values = [];

    }

}


    // ==================================================
    // CHECK DATA
    // ==================================================

    if (
        ctx &&
        typeof Chart !== "undefined" &&
        labels.length > 0 &&
        values.length > 0
    ) {


        // ==================================================
        // CREATE REAL EXPENSE CHART
        // ==================================================

        new Chart(ctx, {


            type: "doughnut",


            data: {


                labels: labels,


                datasets: [{

                    label: "Expense",

                    data: values,


                    // Green colors matching our UI

                    backgroundColor: [

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
                        "rgba(255,255,255,0.85)",


                    borderWidth: 3,


                    hoverOffset: 12

                }]

            },


            options: {


                responsive: true,


                maintainAspectRatio: false,


                // Creates modern doughnut style

                cutout: "68%",


                animation: {

                    duration: 900

                },


                plugins: {


                    // ======================================
                    // LEGEND
                    // ======================================

                    legend: {


                        position: "bottom",


                        labels: {


                            color: "#586356",


                            padding: 20,


                            usePointStyle: true,


                            pointStyle: "circle",


                            boxWidth: 10,


                            font: {

                                size: 12,

                                family:
                                    "Arial, Helvetica, sans-serif"

                            }

                        }

                    },


                    // ======================================
                    // TOOLTIP
                    // ======================================

                    tooltip: {


                        backgroundColor:
                            "rgba(30,45,30,0.88)",


                        padding: 12,


                        cornerRadius: 10,


                        callbacks: {


                            label: function (context) {


                                let value =
                                    Number(context.raw);


                                return (
                                    context.label +
                                    ": ₹" +
                                    value.toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2
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


        // ==================================================
        // NO EXPENSE DATA
        // ==================================================

        if (ctx) {

            ctx.style.display = "none";

        }


        if (noDataMessage) {

            noDataMessage.style.display = "block";

        }

    }



    // ==================================================
    // GLASS CARD HOVER
    // ==================================================

    const cards =
        document.querySelectorAll(".card");


    cards.forEach(function (card) {


        card.addEventListener(
            "mouseenter",
            function () {

                card.style.transform =
                    "translateY(-7px)";

            }
        );


        card.addEventListener(
            "mouseleave",
            function () {

                card.style.transform =
                    "translateY(0px)";

            }
        );


    });


});