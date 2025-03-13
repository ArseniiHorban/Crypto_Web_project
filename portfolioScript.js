// Функція для генерації випадкового кольору у форматі HEX
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Функція для завантаження даних з бекенду (mockPortfolio.json)
async function loadPortfolioData() {
    try {
        const response = await fetch('/public/mockPortfolio.json'); // Шлях до файлу з даними
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error loading portfolio data:', error);
        alert('Failed to load portfolio data. Check console for details.');
        return null;
    }
}

// Ініціалізація графіка
const ctx = document.getElementById('portfolioChart').getContext('2d');
let portfolioChart;

// Функція для оновлення графіка на основі даних
function updateChart(data) {
    if (portfolioChart) {
        portfolioChart.destroy(); // Видаляємо старий графік, якщо він існує
    }

    // Генеруємо випадкові кольори для кожної валюти
    const backgroundColors = data.labels.map(() => getRandomColor());

    portfolioChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Portfolio Allocation',
                data: data.allocations,
                backgroundColor: backgroundColors, // Використовуємо випадкові кольори
                hoverOffset: 4
            }]
        },
        options: {
            plugins: {
                legend: {
                    labels: {
                        color: '#fff', // Білий колір тексту для легенди
                        font: {
                            size: 14 // Розмір тексту
                        }
                    }
                },
                tooltip: {
                    bodyColor: '#fff', // Білий колір тексту в підказках
                    titleColor: '#fff', // Білий колір заголовків в підказках
                    backgroundColor: '#333', // Темний фон для підказок
                    borderColor: '#fff', // Білий колір рамки підказок
                    borderWidth: 1
                }
            }
        }
    });
}

// Функція для заповнення таблиці даними
function populateTable(data) {
    const tableBody = document.getElementById('portfolioTable');
    tableBody.innerHTML = ''; // Очищаємо таблицю

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

    // Додаємо новий рядок до таблиці
    const tableBody = document.getElementById('portfolioTable');
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td>${ticker}</td>
        <td>${name}</td>
        <td><input type="number" class="form-control allocation-input" value="${allocation}" min="0" max="100"></td>
        <td><button class="btn btn-danger btn-sm" onclick="removeRow(this)">Remove</button></td>
    `;
    tableBody.appendChild(newRow);

    // Оновлюємо графік
    updateChartFromInputs();

    // Закриваємо модальне вікно
    const modal = bootstrap.Modal.getInstance(document.getElementById('addCurrencyModal'));
    modal.hide();

    // Очищаємо поля форми
    document.getElementById('tickerInput').value = '';
    document.getElementById('nameInput').value = '';
    document.getElementById('allocationInput').value = '';
}

// Функція для видалення рядка
function removeRow(button) {
    const row = button.closest('tr');
    row.remove();
    updateChartFromInputs(); // Оновлюємо графік після видалення рядка
}

// Завантаження даних при завантаженні сторінки
window.onload = async () => {
    const portfolioData = await loadPortfolioData();
    if (portfolioData) {
        populateTable(portfolioData); // Заповнюємо таблицю
        updateChart(portfolioData); // Оновлюємо графік
    }
};