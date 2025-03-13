// Ініціалізація графіка
const ctx = document.getElementById('priceChart').getContext('2d');
const priceChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Bitcoin Price (USD)',
            data: [],
            borderColor: '#00ffff',
            backgroundColor: 'rgba(0, 255, 255, 0.2)',
            fill: true,
            tension: 0.1
        }]
    },
    options: {
        scales: {
            x: {
                title: { display: true, text: 'Date' },
                ticks: { color: '#fff' }
            },
            y: {
                title: { display: true, text: 'Price (USD)' },
                ticks: { color: '#fff' },
                beginAtZero: false
            }
        },
        plugins: {
            legend: { labels: { color: '#fff' } }
        }
    }
});

// Завантаження початкових даних із заглушки
async function loadInitialData(platform) {
    try {
        const response = await fetch('/public/mockMarket.json');
        const data = await response.json();
        const platformData = data.platforms[platform].data;

        priceChart.data.labels = platformData.map(item => item.date);
        priceChart.data.datasets[0].data = platformData.map(item => item.price);
        priceChart.update();
    } catch (error) {
        console.error('Error loading mock data:', error);
    }
}

// Функція для оновлення графіка
function updateChart(platform) {
    document.querySelectorAll('.platform-item').forEach(item => item.classList.remove('active'));
    event.target.classList.add('active');
    loadInitialData(platform); // Завантажуємо початкові дані для обраної платформи
    console.log(`Selected platform: ${platform}`);
}

// Функція для генерації нового значення ціни (імітація оновлення)
function generateNewPrice(lastPrice) {
    const change = (Math.random() - 0.5) * 200; // Випадкова зміна від -100 до +100
    return Math.max(90000, Math.min(110000, lastPrice + change)); // Обмеження між 90,000 і 110,000
}

// Функція для оновлення даних із затримкою
function updateChartData() {
    const now = new Date();
    const label = now.toLocaleDateString(); // Нова дата
    const lastPrice = priceChart.data.datasets[0].data.length > 0 ? priceChart.data.datasets[0].data[priceChart.data.datasets[0].data.length - 1] : 97500;
    const newPrice = generateNewPrice(lastPrice);

    // Додаємо нові дані
    priceChart.data.labels.push(label);
    priceChart.data.datasets[0].data.push(newPrice);

    // Обмеження до 30 точок
    if (priceChart.data.labels.length > 30) {
        priceChart.data.labels.shift();
        priceChart.data.datasets[0].data.shift();
    }

    priceChart.update();
}

// Оновлення графіка кожні 5 секунд
setInterval(updateChartData, 5000); // 5000 мс = 5 секунд

// Ініціалізація з платформи Binance за замовчуванням
loadInitialData('Binance');