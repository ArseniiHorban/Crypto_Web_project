// Generate a random HEX color
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Populate the Highlights section with performance metrics
function populateHighlights(performance) {
    document.getElementById('sharpeRatio').textContent = performance.sharpe_ratio.toFixed(2);
    document.getElementById('annualVolatility').textContent = (performance.annual_volatility).toFixed(2) + '%';
    document.getElementById('maxDrawdown').textContent = (performance.max_drawdown).toFixed(2) + '%';
}

// Initialize the Portfolio Allocation chart
let portfolioChart;
function updateChart(labels, allocations) {
    const ctx = document.getElementById('portfolioChart').getContext('2d');
    if (portfolioChart) {
        portfolioChart.destroy();
    }

    const backgroundColors = labels.map(() => getRandomColor());

    portfolioChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Portfolio Allocation',
                data: allocations,
                backgroundColor: backgroundColors,
                hoverOffset: 4
            }]
        },
        options: {
            plugins: {
                legend: {
                    labels: {
                        color: '#fff',
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    bodyColor: '#fff',
                    titleColor: '#fff',
                    backgroundColor: '#333',
                    borderColor: '#fff',
                    borderWidth: 1
                }
            }
        }
    });
}

// Initialize the Portfolio Growth chart
let portfolioGrowthChart;
function initializePortfolioGrowthChart(portfolioValue) {
    const growthCtx = document.getElementById('portfolioGrowthChart').getContext('2d');
    if (portfolioGrowthChart) {
        portfolioGrowthChart.destroy();
    }

    const dates = Object.keys(portfolioValue);
    const values = Object.values(portfolio_value);

    portfolioGrowthChart = new Chart(growthCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Portfolio Value',
                data: values,
                borderColor: '#36a2eb',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    ticks: {
                        color: '#fff',
                        maxTicksLimit: 10 // Limit the number of ticks for readability
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#fff'
                    }
                },
                tooltip: {
                    bodyColor: '#fff',
                    titleColor: '#fff',
                    backgroundColor: '#333',
                    borderColor: '#fff',
                    borderWidth: 1
                }
            }
        }
    });
}

// Initialize the page on load
window.onload = () => {
    const labels = {{ labels|safe }};
    const allocations = {{ allocations|safe }};
    const performance = {{ performance|safe }};
    const portfolioValue = {{ portfolio_value|safe }};
    const annualReturns = {{ annual_returns|safe }};

    populateHighlights(performance);

    if (labels && allocations && labels.length > 0 && allocations.length > 0) {
        updateChart(labels, allocations);
    }

    if (portfolioValue && Object.keys(portfolioValue).length > 0) {
        initializePortfolioGrowthChart(portfolioValue);
    }

    // Populate the Annual Returns table
    const tableBody = document.getElementById('annualReturnsBody');
    tableBody.innerHTML = '';
    annualReturns.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.year}</td>
            <td>${item.portfolio_return.toFixed(2)}%</td>
            <td>$${item.portfolio_balance.toFixed(0)}</td>
        `;
        tableBody.appendChild(row);
    });
};