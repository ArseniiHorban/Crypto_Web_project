// Функція для перемикання між Register і Login
function switchToRegister() {
    const nameField = document.getElementById('nameField');
    const nameInput = document.getElementById('name');
    nameField.classList.remove('d-none');
    nameInput.setAttribute('required', 'required'); // Додаємо required для Register
    document.getElementById('submitBtn').textContent = 'Register';
    document.getElementById('forgotLink').classList.add('d-none');
}

function switchToLogin() {
    const nameField = document.getElementById('nameField');
    const nameInput = document.getElementById('name');
    nameField.classList.add('d-none');
    nameInput.removeAttribute('required'); // Прибираємо required для Login
    document.getElementById('submitBtn').textContent = 'Login';
    document.getElementById('forgotLink').classList.remove('d-none');
}

// Виклик за замовчуванням
switchToRegister();

// Обробка форми
document.getElementById('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const isRegister = document.getElementById('submitBtn').textContent === 'Register';

    const data = isRegister ? { name, email, password } : { email, password };

    try {
        const mockData = await (await fetch('public/mockData.json')).json();

        if (isRegister) {
            alert('Mock registration: ' + JSON.stringify(mockData.registerSuccess));
        } else {
            const user = mockData.users.find(u => u.email === email && u.password === password);
            if (user) {
                alert('Login successful! User data: ' + JSON.stringify(mockData.loginSuccess));
            } else {
                alert('Login failed! Please check your email or password. Valid users:\n' +
                    mockData.users.map(u => `${u.email}: ${u.password}`).join('\n'));
            }
        }
    } catch (error) {
        alert('Error: Failed to load mock data or process request. ' + error.message);
    }
});