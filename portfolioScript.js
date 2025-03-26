// Функція для генерації випадкового кольору у форматі HEX
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Функція для завантаження даних із portfolioData.json
async function loadPortfolioData() {
    try {
        const response = await fetch('/public/portfolioData.json');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return {
            tickers: Object.keys(data.data.assets),
            labels: Object.keys(data.data.assets),
            allocations: Object.values(data.data.assets),
            performance: data.performance,
            portfolioValue: data.portfolio_value // Додаємо portfolio_value для графіка
        };
    } catch (error) {
        console.error('Error loading portfolio data:', error);
        alert('Failed to load portfolio data. Check console for details.');
        return null;
    }
}

// Функція для заповнення Highlights
function populateHighlights(performance) {
    // Sharpe Ratio
    document.getElementById('sharpeRatio').textContent = performance.sharpe_ratio.toFixed(2);

    // Annual Volatility (переводимо у відсотки)
    document.getElementById('annualVolatility').textContent = (performance.annual_volatility * 100).toFixed(2) + '%';

    // Max Drawdown (переводимо у відсотки, прибираємо мінус)
    document.getElementById('maxDrawdown').textContent = (performance.max_drawdown * 100).toFixed(2) + '%';
}

// Ініціалізація графіка Portfolio Allocation
const ctx = document.getElementById('portfolioChart').getContext('2d');
let portfolioChart;

// Функція для оновлення графіка Portfolio Allocation
function updateChart(data) {
    if (portfolioChart) {
        portfolioChart.destroy();
    }

    const backgroundColors = data.labels.map(() => getRandomColor());

    portfolioChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Portfolio Allocation',
                data: data.allocations,
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

// Функція для ініціалізації графіка Portfolio Growth
let portfolioGrowthChart;
function initializePortfolioGrowthChart(portfolioValue) {
    const growthCtx = document.getElementById('portfolioGrowthChart').getContext('2d');
    if (portfolioGrowthChart) {
        portfolioGrowthChart.destroy();
    }

    const dates = Object.keys(portfolioValue);
    const values = Object.values(portfolioValue);

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
                        maxTicksLimit: 10 // Обмежуємо кількість міток для читабельності
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

// Функція для заповнення таблиці даними
function populateTable(data) {
    const tableBody = document.getElementById('portfolioTable');
    tableBody.innerHTML = '';

    data.labels.forEach((label, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${data.tickers[index]}</td>
            <td>${label}</td>
            <td><input type="number" class="form-control allocation-input" value="${data.allocations[index]}" min="0" max="100"></td>
            <td><button class="btn btn-danger btn-sm" onclick="removeRow(this)">Remove</button></td>
        `;
        tableBody.appendChild(row);
    });
}

// Функція для оновлення графіка на основі введених даних
function updateChartFromInputs() {
    const inputs = document.querySelectorAll('.allocation-input');
    const newData = {
        labels: [],
        allocations: []
    };

    document.querySelectorAll('#portfolioTable tr').forEach(row => {
        const ticker = row.cells[0].textContent;
        const name = row.cells[1].textContent;
        const allocation = parseFloat(row.cells[2].querySelector('input').value);

        newData.labels.push(name);
        newData.allocations.push(allocation);
    });

    updateChart(newData);
}

// Функція для додавання нової валюти через модальне вікно
function addNewCurrency() {
    const ticker = document.getElementById('tickerInput').value;
    const name = document.getElementById('nameInput').value;
    const allocation = parseFloat(document.getElementById('allocationInput').value);

    if (!ticker || !name || isNaN(allocation)) {
        alert('Please fill in all fields correctly.');
        return;
    }

    const tableBody = document.getElementById('portfolioTable');
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td>${ticker}</td>
        <td>${name}</td>
        <td><input type="number" class="form-control allocation-input" value="${allocation}" min="0" max="100"></td>
        <td><button class="btn btn-danger btn-sm" onclick="removeRow(this)">Remove</button></td>
    `;
    tableBody.appendChild(newRow);

    updateChartFromInputs();

    const modal = bootstrap.Modal.getInstance(document.getElementById('addCurrencyModal'));
    modal.hide();

    document.getElementById('tickerInput').value = '';
    document.getElementById('nameInput').value = '';
    document.getElementById('allocationInput').value = '';
}

// Функція для видалення рядка
function removeRow(button) {
    const row = button.closest('tr');
    row.remove();
    updateChartFromInputs();
}

// Додаємо нові функції для Annual Returns
async function loadAnnualReturnsData() {
    try {
        const response = await fetch('/public/annualReturns.json');
        const data = await response.json();
        return data.annualReturns;
    } catch (error) {
        console.error('Error loading annual returns data:', error);
        return null;
    }
}

function populateAnnualReturnsTable(data) {
    const tableBody = document.getElementById('annualReturnsBody');
    tableBody.innerHTML = '';

    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.year}</td>
            <td>${item.inflation}</td>
            <td>${item.portfolioReturn}</td>
            <td>${item.portfolioBalance}</td>
            <td>${item.SP500Return}</td>
            <td>${item.SP500Balance}</td>
            <td>${item.VTI}</td>
            <td>${item.VNQ}</td>
            <td>${item.VXUS}</td>
            <td>${item.BND}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Завантаження даних при завантаженні сторінки
window.onload = async () => {
    const portfolioData = await loadPortfolioData();
    if (portfolioData) {
        populateTable(portfolioData);
        updateChart(portfolioData);
        populateHighlights(portfolioData.performance);
        initializePortfolioGrowthChart(portfolioData.portfolioValue); // Ініціалізація графіка Portfolio Growth
    }

    const annualReturnsData = await loadAnnualReturnsData();
    if (annualReturnsData) {
        populateAnnualReturnsTable(annualReturnsData);
    }
};