// Функція для завантаження та відображення даних про криптовалюти
async function loadCryptoData() {
    try {
        const response = await fetch('/public/mockCrypto.json');
        const data = await response.json();
        const tableBody = document.getElementById('tableBody');

        // Очищаємо таблицю
        tableBody.innerHTML = '';

        // Заповнюємо таблицю даними
        data.cryptos.forEach(crypto => {
            const row = document.createElement('tr');
            row.innerHTML = `
        <td>${crypto.name}</td>
        <td>${crypto.price}</td>
        <td>${crypto.directVol}</td>
        <td>${crypto.totalVol}</td>
        <td>${crypto.topTierVol}</td>
      `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading crypto data:', error);
        alert('Failed to load crypto data. Check console for details.');
    }
}

// Виклик функції при завантаженні сторінки
window.onload = loadCryptoData;