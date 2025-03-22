// Logs when the script is loaded
console.log('homeScript.js loaded');

// Global variable to store the chart instance
let chartInstance = null;

// Function to fetch data with caching to avoid repeated API calls
async function fetchWithCache(url, cacheKey, cacheDuration) {
    console.log('fetchWithCache called');
    const cachedData = localStorage.getItem(cacheKey);
    const cachedTime = localStorage.getItem(`${cacheKey}_time`);
    const now = new Date().getTime();

    // Return cached data if it exists and is not expired
    if (cachedData && cachedTime && (now - cachedTime) < cacheDuration) {
        return JSON.parse(cachedData);
    }

    // Fetch new data if cache is expired or doesn't exist
    const response = await fetch(url);
    const data = await response.json();
    localStorage.setItem(cacheKey, JSON.stringify(data));
    localStorage.setItem(`${cacheKey}_time`, now.toString());
    return data;
}

// Function to fetch cryptocurrency data and update the table and Bitcoin stats
async function fetchCryptoData() {
    console.log('fetchCryptoData called');
    try {
        // Fetch top 10 cryptocurrencies from CoinGecko API with additional price change intervals
        const data = await fetchWithCache(
            'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false&price_change_percentage=1h%2C24h%2C7d%2C14d%2C30d%2C200d%2C1y',
            'crypto_markets',
            5 * 60 * 1000 // Cache for 5 minutes
        );

        // Update the table with cryptocurrency data
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
                <td style="color: ${coin.price_change_percentage_24h >= 0 ? '#00ff00' : '#ff0000'}">
                    ${coin.price_change_percentage_24h ? coin.price_change_percentage_24h.toFixed(2) + '%' : 'N/A'}
                </td>
            `;
            tableBody.appendChild(row);

            // Update Bitcoin stats if the coin is Bitcoin
            if (coin.id === 'bitcoin') {
                const btcPriceChange = document.getElementById('btcPriceChange');
                const btcMarketCap = document.getElementById('btcMarketCap');
                const btcVolume = document.getElementById('btcVolume');
                const btcAth = document.getElementById('btcAth');
                const btcAtl = document.getElementById('btcAtl');
                const btcPriceChange7d = document.getElementById('btcPriceChange7d');
                const btcPriceChange30d = document.getElementById('btcPriceChange30d');
                const btcPriceChange1y = document.getElementById('btcPriceChange1y');

                btcPriceChange.textContent = coin.price_change_percentage_24h
                    ? `${coin.price_change_percentage_24h.toFixed(2)}%`
                    : 'N/A';
                btcPriceChange.style.color = coin.price_change_percentage_24h >= 0 ? '#00ff00' : '#ff0000';

                btcMarketCap.textContent = coin.market_cap
                    ? `$${coin.market_cap.toLocaleString()}`
                    : 'N/A';

                btcVolume.textContent = coin.total_volume
                    ? `$${coin.total_volume.toLocaleString()}`
                    : 'N/A';

                btcAth.textContent = coin.ath
                    ? `$${coin.ath.toLocaleString()} (${new Date(coin.ath_date).toLocaleDateString()})`
                    : 'N/A';

                btcAtl.textContent = coin.atl
                    ? `$${coin.atl.toLocaleString()} (${new Date(coin.atl_date).toLocaleDateString()})`
                    : 'N/A';

                // Use the correct field names for price changes
                btcPriceChange7d.textContent = coin.price_change_percentage_7d_in_currency
                    ? `${coin.price_change_percentage_7d_in_currency.toFixed(2)}%`
                    : 'N/A';
                btcPriceChange7d.style.color = coin.price_change_percentage_7d_in_currency >= 0 ? '#00ff00' : '#ff0000';

                btcPriceChange30d.textContent = coin.price_change_percentage_30d_in_currency
                    ? `${coin.price_change_percentage_30d_in_currency.toFixed(2)}%`
                    : 'N/A';
                btcPriceChange30d.style.color = coin.price_change_percentage_30d_in_currency >= 0 ? '#00ff00' : '#ff0000';

                btcPriceChange1y.textContent = coin.price_change_percentage_1y_in_currency
                    ? `${coin.price_change_percentage_1y_in_currency.toFixed(2)}%`
                    : 'N/A';
                btcPriceChange1y.style.color = coin.price_change_percentage_1y_in_currency >= 0 ? '#00ff00' : '#ff0000';
            }
        });
        totalMarketVolume.textContent = `$${totalVolume.toLocaleString()}`;
    } catch (error) {
        console.error('Error fetching data for table:', error);
    }
}

// Function to fetch trending coins and update the trending section
async function fetchTrendingCoins() {
    console.log('fetchTrendingCoins called');
    try {
        // Fetch trending coins from CoinGecko API
        const trendingData = await fetchWithCache(
            'https://api.coingecko.com/api/v3/search/trending',
            'trending_coins',
            5 * 60 * 1000 // Cache for 5 minutes
        );

        // Get the IDs of the trending coins
        const trendingCoinIds = trendingData.coins.map(coin => coin.item.id).join(',');

        // Fetch detailed data for trending coins to get price change
        const detailedData = await fetchWithCache(
            `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=${trendingCoinIds}&order=market_cap_desc&per_page=10&page=1&sparkline=false&price_change_percentage=24h`,
            'trending_coins_detailed',
            5 * 60 * 1000 // Cache for 5 minutes
        );

        // Update the trending coins section
        const trendingBody = document.getElementById('trendingBody');
        trendingBody.innerHTML = '';

        // Get the top 6 trending coins (changed from 10 to 6)
        const trendingCoins = detailedData.slice(0, 6);
        trendingCoins.forEach(coin => {
            const row = document.createElement('div');
            row.className = 'col-6 col-md-3 col-lg-2 text-center mb-3';
            row.innerHTML = `
                <div class="trending-coin">
                    <img src="${coin.image}" alt="${coin.name}" class="coin-img mb-2">
                    <p class="mb-1">${coin.name} (${coin.symbol.toUpperCase()})</p>
                    <p style="color: ${coin.price_change_percentage_24h_in_currency >= 0 ? '#00ff00' : '#ff0000'}">
                        ${coin.price_change_percentage_24h_in_currency ? coin.price_change_percentage_24h_in_currency.toFixed(2) + '%' : 'N/A'}
                    </p>
                </div>
            `;
            trendingBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching trending coins:', error);
    }
}

// Function to update the Bitcoin price chart
window.updateChart = async function(days) {
    console.log(`Updating chart for ${days} days`);
    try {
        // Update active button state
        const buttons = document.querySelectorAll('.chart-controls .btn');
        buttons.forEach(btn => btn.classList.remove('active'));
        const activeButton = Array.from(buttons).find(btn => btn.textContent.includes(days === 1 ? '1 Day' : days === 7 ? '7 Days' : '1 Year'));
        if (activeButton) activeButton.classList.add('active');

        // Fetch Bitcoin price history from CoinGecko API
        const bitcoinData = await fetchWithCache(
            `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=${days}`,
            `bitcoin_chart_${days}`,
            5 * 60 * 1000 // Cache for 5 minutes
        );

        // Prepare data for the chart
        const prices = bitcoinData.prices.map(price => price[1]);
        const labels = bitcoinData.prices.map((price, index) => {
            const date = new Date(price[0]);
            return days === 1 ? date.toLocaleTimeString() : date.toLocaleDateString();
        });

        // Create or update the chart
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
                    borderColor: '#fff', // White line color
                    backgroundColor: 'rgba(255, 255, 255, 0)',
                    fill: false,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: '#333', // Dark gray grid color
                            drawOnChartArea: true // Enable grid
                        },
                        ticks: {
                            color: '#fff' // White tick labels
                        }
                    },
                    x: {
                        grid: {
                            color: '#333', // Dark gray grid color
                            drawOnChartArea: true // Enable grid
                        },
                        ticks: {
                            color: '#fff', // White tick labels
                            maxTicksLimit: 10
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff' // White legend text
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
        console.error('Error updating chart:', error);
    }
};

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing...');
    fetchCryptoData();
    fetchTrendingCoins();
    window.updateChart(7);
});

console.log('updateChart defined:', typeof window.updateChart);