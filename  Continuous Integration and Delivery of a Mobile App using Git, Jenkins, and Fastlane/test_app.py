# tests/test_app.py
import pytest

try:
    from appium import webdriver
except Exception:
    pytest.skip("Appium not available in CI runner; skipping device tests", allow_module_level=True)

@pytest.fixture
def driver():
    desired_caps = {
        'platformName': 'Android',
        'deviceName': 'emulator-5554',
        'appPackage': 'com.example.myapp',
        'appActivity': '.MainActivity'
    }
    return webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

def test_app_launch(driver):
    driver.launch_app()
    assert driver.find_element_by_xpath("//android.widget.TextView[@text='Hello World!']").is_displayed()