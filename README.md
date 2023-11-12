This project is called Investor. It's a competitive mock investor website designed using Python Flask and JavaScript JQuery. This is a class project for Springboard's Software Engineering Bootcamp.

Investor gets stockmarket data from the free version of the Alpha Advantage API. When you first visit the
site you will be taken to the leaderboard which shows the portfolios with the 10 highest net worths. Each
portfolio is created using $10,000 in cash to buy stocks using data from the Alpha Advantage API. As the
stock data changes over time, the net worth of the portfolio changes.

The website features include: User signup, login, and logout; stock market portfolio creation and a leader
board. You can also edit and delete your user profile and portfolios. There is a search bar to search for other
users. Their profiles and portfolios can also be viewed.

Investor was styled using CSS, Bootstrap, and Font Awesome. Some front end programing is handled using JavaScript
JQuery, but the majority of the programming is backend using Python Flask, Sql-Alchemy, and WTForms.

Added Flask_APScheduler to automate maintenance. The free version of the Alpha Vantage API only allows for 5 API calls every minute and returns daily stock values instead of instant values. Due to this, the app is designed to store stock prices in the database and only call the API when necessary. The APScheduler runs the background, late at night if you are in the US (depends on the timezone), and makes calls to the API to update stock information within the database.