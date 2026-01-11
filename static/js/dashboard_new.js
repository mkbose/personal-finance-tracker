// Simple INR formatting function with commas
function formatINR(amount) {
    return '₹' + amount.toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Test API endpoints
function testAPIs() {
    console.log('Testing API endpoints...');
    
    // Test basic data
    fetch('/api/expenses/test-data')
        .then(response => response.json())
        .then(data => {
            console.log('Test data response:', data);
        })
        .catch(error => console.error('Test data error:', error));
    
    // Test custom range (should show grand total)
    fetch('/api/expenses/custom-range')
        .then(response => response.json())
        .then(data => {
            console.log('Custom range (no dates) response:', data);
        })
        .catch(error => console.error('Custom range error:', error));
}

// Custom date range functions
function calculateCustomRange() {
    const dateFrom = document.getElementById('date_from').value;
    const dateTo = document.getElementById('date_to').value;
    
    if (!dateFrom && !dateTo) {
        // No dates selected, show all-time total
        fetch('/api/expenses/custom-range')
            .then(function(response) {
                console.log('Custom range (all-time) response status:', response.status);
                return response.json();
            })
            .then(function(data) {
                console.log('Custom range (all-time) data:', data);
                document.getElementById('custom-range-total').textContent = formatINR(data.total);
            })
            .catch(function(error) {
                console.error('Error fetching all-time total:', error);
            });
        return;
    }
    
    if (!dateFrom || !dateTo) {
        alert('Please select both From and To dates');
        return;
    }
    
    // Fetch custom range total from API
    fetch(`/api/expenses/custom-range?date_from=${dateFrom}&date_to=${dateTo}`)
        .then(function(response) {
            console.log('Custom range response status:', response.status);
            return response.json();
        })
        .then(function(data) {
            console.log('Custom range data:', data);
            document.getElementById('custom-range-total').textContent = formatINR(data.total);
        })
        .catch(function(error) {
            console.error('Error fetching custom range data:', error);
            alert('Error calculating custom range total');
        });
}

function clearCustomRange() {
    document.getElementById('date_from').value = '';
    document.getElementById('date_to').value = '';
    // Reset to all-time total
    calculateCustomRange();
}

// Debug: Log data to console
console.log('Category breakdown:', {{ category_breakdown | tojson | safe }});
console.log('Monthly total:', {{ monthly_total }});
console.log('Recent total:', {{ recent_total }});
console.log('Total expenses:', {{ total_expenses }});

// Test APIs on page load
testAPIs();

// Initialize custom range with all-time total
calculateCustomRange();

// Category breakdown chart
const categoryData = {{ category_breakdown | tojson | safe }};
console.log('Parsed categoryData:', categoryData);
console.log('CategoryData length:', categoryData ? categoryData.length : 'null');

if (categoryData && categoryData.length > 0) {
    console.log('Rendering category chart...');
    var categoryValues = [];
    var categoryLabels = [];
    for (var i = 0; i < categoryData.length; i++) {
        categoryValues.push(categoryData[i].total);
        categoryLabels.push(categoryData[i].name);
    }
    console.log('Category values:', categoryValues);
    console.log('Category labels:', categoryLabels);

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
    console.log('No category data available');
    // Show no data message
    document.getElementById('categoryChart').innerHTML = '<div class="text-center text-muted py-5">No expense data available. Add some expenses to see the breakdown.</div>';
}

// Monthly trend chart
console.log('Fetching monthly trend data...');
fetch('/api/expenses/monthly-trend')
    .then(function(response) {
        console.log('Trend response status:', response.status);
        return response.json();
    })
    .then(function(data) {
        console.log('Trend data received:', data);
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
                title: 'Amount (₹)',
                tickformat: '₹,.2f'
            }
        };

        console.log('Rendering trend chart...');
        Plotly.newPlot('trendChart', [trendTrace], trendLayout);
    })
    .catch(function(error) {
        console.error('Error fetching trend data:', error);
    });
