console.log('homeScript.js loaded'); // Для отладки

let chartInstance = null;

async function fetchWithCache(url, cacheKey, cacheDuration) {
    console.log('fetchWithCache called');
    const cachedData = localStorage.getItem(cacheKey);
    const cachedTime = localStorage.getItem(`${cacheKey}_time`);
    const now = new Date().getTime();

    if (cachedData && cachedTime && (now - cachedTime) < cacheDuration) {
        return JSON.parse(cachedData);
    }

    const response = await fetch(url);
    const data = await response.json();
    localStorage.setItem(cacheKey, JSON.stringify(data));
    localStorage.setItem(`${cacheKey}_time`, now.toString());
    return data;
}

async function fetchCryptoData() {
    console.log('fetchCryptoData called');
    try {
        const data = await fetchWithCache(
            'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false',
            'crypto_markets',
            5 * 60 * 1000
        );

        const tableBody = document.getElementById('tableBody');
        const totalMarketVolume = document.getElementById('totalMarketVolume');
        tableBody.innerHTML = '';

        let totalVolume = 0;
        data.forEach(coin => {
            totalVolume += coin.total_volume;
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${coin.name}</td>
                <td>$${coin.current_price ? coin.current_price.toLocaleString() : 'N/A'}</td>
                <td>$${coin.total_volume ? coin.total_volume.toLocaleString() : 'N/A'}</td>
                <td>$${coin.circulating_supply ? coin.circulating_supply.toLocaleString() : 'N/A'}</td>
                <td>$${coin.market_cap ? coin.market_cap.toLocaleString() : 'N/A'}</td>
            `;
            tableBody.appendChild(row);
        });
        totalMarketVolume.textContent = `$${totalVolume.toLocaleString()}`;
    } catch (error) {
        console.error('Помилка при отриманні даних для таблиці:', error);
    }
}

window.updateChart = async function(days) {
    console.log(`Updating chart for ${days} days`);
    try {
        const buttons = document.querySelectorAll('.chart-controls .btn');
        buttons.forEach(btn => btn.classList.remove('active'));
        const activeButton = Array.from(buttons).find(btn => btn.textContent === (days === 1 ? '1 Day' : days === 7 ? '7 Days' : '1 Year'));
        if (activeButton) activeButton.classList.add('active');

        const bitcoinData = await fetchWithCache(
            `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=${days}`,
            `bitcoin_chart_${days}`,
            5 * 60 * 1000
        );

        const prices = bitcoinData.prices.map(price => price[1]);
        const labels = bitcoinData.prices.map((price, index) => {
            const date = new Date(price[0]);
            return days === 1 ? date.toLocaleTimeString() : date.toLocaleDateString();
        });

        const ctx = document.getElementById('bitcoinChart').getContext('2d');
        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Bitcoin Price (USD)',
                    data: prices,
                    borderColor: '#ff69b4',
                    backgroundColor: 'rgba(255, 255, 255, 0)', // Полностью прозрачный фон
                    fill: false, // Отключаем заливку
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            drawOnChartArea: false // Отключаем фон сетки
                        },
                        ticks: {
                            color: '#fff'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            drawOnChartArea: false // Отключаем фон сетки
                        },
                        ticks: {
                            color: '#fff',
                            maxTicksLimit: 10
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff'
                        }
                    }
                },
                elements: {
                    point: {
                        backgroundColor: 'transparent'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Помилка при оновленні графіка:', error);
    }
};

// Инициализация при загрузке DOM
console.log('Adding DOMContentLoaded listener');
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing...');
    fetchCryptoData();
    window.updateChart(7);
});

// Дополнительная отладка
console.log('updateChart defined:', typeof window.updateChart);