import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    browser.maximize_window()
    yield browser
    browser.quit()


BASE_URL = "http://127.0.0.1:5000"


def test_dashboard_loads(driver):
    driver.get(BASE_URL)

    assert "Dashboard" in driver.page_source
    assert "Total income" in driver.page_source
    assert "Total expenses" in driver.page_source
    assert "Available balance" in driver.page_source


def test_transactions_page_loads(driver):
    driver.get(BASE_URL + "/transactions")

    assert "Transaction History" in driver.page_source


def test_add_income_page_loads(driver):
    driver.get(BASE_URL + "/add-income")

    assert driver.find_element(By.NAME, "source")
    assert driver.find_element(By.NAME, "amount")
    assert driver.find_element(By.NAME, "date")


def test_add_expense_page_loads(driver):
    driver.get(BASE_URL + "/add-expense")

    assert driver.find_element(By.NAME, "title")
    assert driver.find_element(By.NAME, "amount")
    assert driver.find_element(By.NAME, "category")
    assert driver.find_element(By.NAME, "date")


def test_monthly_summary_page_loads(driver):
    driver.get(BASE_URL + "/monthly-summary")

    assert "Monthly Summary" in driver.page_source