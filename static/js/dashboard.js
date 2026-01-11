// Simple USD formatting function
function formatUSD(amount) {
    return '$' + amount.toFixed(2);
}

// Debug: Log data to console
console.log('Category breakdown:', {{ category_breakdown | tojson | safe }});
console.log('Monthly total:', {{ monthly_total }});
console.log('Recent total:', {{ recent_total }});
console.log('Total expenses:', {{ total_expenses }});

// Category breakdown chart
const categoryData = {{ category_breakdown | tojson | safe }};
if (categoryData && categoryData.length > 0) {
    var categoryValues = [];
    var categoryLabels = [];
    for (var i = 0; i < categoryData.length; i++) {
        categoryValues.push(categoryData[i].total);
        categoryLabels.push(categoryData[i].name);
    }

    var categoryTrace = {
        values: categoryValues,
        labels: categoryLabels,
        type: 'pie',
        marker: {
            colors: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        }
    };

    var categoryLayout = {
        margin: { t: 0, b: 0, l: 0, r: 0 }
    };

    Plotly.newPlot('categoryChart', [categoryTrace], categoryLayout);
} else {
    // Show no data message
    document.getElementById('categoryChart').innerHTML = '<div class="text-center text-muted py-5">No expense data available. Add some expenses to see the breakdown.</div>';
}

// Monthly trend chart
fetch('/api/expenses/monthly-trend')
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        var trendTrace = {
            x: data.map(function(d) { return d.month; }),
            y: data.map(function(d) { return d.total; }),
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#007bff' }
        };

        var trendLayout = {
            margin: { t: 20, b: 40, l: 60, r: 20 },
            xaxis: { title: 'Month' },
            yaxis: { 
                title: 'Amount ($)',
                tickformat: '$,.2f'
            }
        };

        Plotly.newPlot('trendChart', [trendTrace], trendLayout);
    });
