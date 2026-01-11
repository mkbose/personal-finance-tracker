// Main JavaScript file for Personal Finance Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(function() {
            card.style.transition = 'opacity 0.5s, transform 0.5s';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Format currency inputs
    const amountInputs = document.querySelectorAll('input[type="number"][name*="amount"]');
    amountInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('a[href*="delete"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Dynamic subcategory loading
    const categorySelects = document.querySelectorAll('select[name="category_id"]');
    categorySelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const categoryId = this.value;
            const subcategorySelect = document.getElementById('subcategory-select');
            
            if (subcategorySelect) {
                // Clear existing options
                subcategorySelect.innerHTML = '<option value="0">None</option>';
                
                if (categoryId) {
                    fetch(`/categories/${categoryId}/subcategories/json`)
                        .then(response => response.json())
                        .then(subcategories => {
                            subcategories.forEach(sub => {
                                const option = document.createElement('option');
                                option.value = sub.id;
                                option.textContent = sub.name;
                                subcategorySelect.appendChild(option);
                            });
                        })
                        .catch(error => console.error('Error fetching subcategories:', error));
                }
            }
        });
    });
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Chart helper functions
function createPieChart(elementId, data, labels) {
    const trace = {
        values: data,
        labels: labels,
        type: 'pie',
        marker: {
            colors: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        }
    };

    const layout = {
        margin: { t: 0, b: 0, l: 0, r: 0 },
        showlegend: true,
        legend: {
            position: 'right'
        }
    };

    Plotly.newPlot(elementId, [trace], layout, {responsive: true});
}

function createLineChart(elementId, xData, yData, title = '') {
    const trace = {
        x: xData,
        y: yData,
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: '#007bff' }
    };

    const layout = {
        title: title,
        margin: { t: 40, b: 40, l: 60, r: 20 },
        xaxis: { title: 'Month' },
        yaxis: { title: 'Amount ($)' },
        responsive: true
    };

    Plotly.newPlot(elementId, [trace], layout, {responsive: true});
}
