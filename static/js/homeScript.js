// Global variable to store the Bitcoin chart instance
let bitcoinChart;

// Function to update the Bitcoin price chart based on the selected time period
function updateChart(days) {
    const ctx = document.getElementById('bitcoinChart').getContext('2d');
    const data = bitcoinChartData[days];

    // Destroy the existing chart if it exists
    if (bitcoinChart) {
        bitcoinChart.destroy();
    }

    // Create a new chart
    bitcoinChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Bitcoin Price (USD)',
                data: data.prices,
                borderColor: '#FFFFFF', // Changed to white
                fill: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            },
            plugins: {
                legend: { labels: { color: '#fff' } }
            }
        }
    });

    // Update active button styling
    document.querySelectorAll('.chart-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.chart-btn[onclick="updateChart(${days})"]`).classList.add('active');
}

// Initialize mini-charts for each coin in the Top Cryptocurrencies table
document.addEventListener('DOMContentLoaded', function() {
    Object.keys(historicalData).forEach(coinId => {
        const ctx = document.getElementById(`chart-${coinId}`);
        if (ctx) {  // Check if the canvas element exists
            const data = historicalData[coinId];
            new Chart(ctx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: data.dates.slice(-30), // Last 30 days
                    datasets: [{
                        label: '',
                        data: data.prices.slice(-30),
                        borderColor: '#FFFFFF', // Changed to white
                        fill: false,
                        pointRadius: 0,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { display: false },
                        y: { display: false }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    });

    // Initialize the Bitcoin chart with 7 days by default
    updateChart(7);
});