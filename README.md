# Crypto Web Project
Crypto Web Project is a demonstration web application for tracking a cryptocurrency portfolio. It allows users to view asset allocation, key performance metrics (e.g., Sharpe Ratio, Volatility, Max Drawdown), and portfolio growth through interactive charts and tables.

---

## Technologies

The project is built using a modern stack for both frontend and backend development:

- **HTML5**: Structure of web pages (`home.html`, `market.html`, `portfolio.html`, `registration.html`).
- **CSS3**: Styling of pages via separate files (`common.css`, `home.css`, `market.css`, `portfolio.css`, `registration.css`) with responsive design using media queries.
- **JavaScript**: Dynamic logic and interactivity (`homeScript.js`, `marketScript.js`, `portfolioScript.js`, `registrationScript.js`) with asynchronous programming (`async/await`).
- **Bootstrap 5.3.3**: Framework for responsive design and pre-built components (navigation, tables, modals).
- **Chart.js**: Library for creating interactive charts (pie chart for asset allocation, line chart for portfolio growth).
- **Django**: Backend framework that can be used for request handling, data management, and database integration.
- **Redis**: In-memory database for caching and fast data access.
- **PostgreSQL**: Relational database for storing structured data about the portfolio, users, etc.

---

## Setup Instructions

To run the project locally, follow these steps:

1. **Clone the repository**  
   Clone this repository to your local machine and ensure you have all required files, including the `.env` file (provided separately, not available on GitHub).

2. **Install Docker Desktop**  
   If not already installed, download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for your operating system.

3. **Open the project in an IDE**  
   Open the project folder in Visual Studio, VS Code, PyCharm, or your preferred IDE.

4. **Build and start the containers**  
   In the terminal, navigate to the project directory and run the following command to build and start the Docker containers:  
```bash
   docker-compose up --build
```

5. **Access the application**  
Open your browser and navigate to `http://localhost:8000` to view the running application.

---

## Conclusion

Crypto Web Project is a well-structured demonstration application for tracking a cryptocurrency portfolio. It is ready for expansion through API integration and backend development, making it a fully functional tool for real-world use.
