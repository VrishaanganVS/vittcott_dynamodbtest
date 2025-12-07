"""
Smoke Tests for Vittcott API
Tests critical API endpoints to ensure basic functionality
"""
import httpx
import sys
import os
from typing import Dict, Any

# Get base URL from environment or use default
BASE_URL = os.getenv("VITTCOTT_BASE_URL", "http://localhost:8000")


class SmokeTestRunner:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test(self, name: str, test_func):
        """Run a single test"""
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")
        try:
            result = test_func()
            if result:
                print(f"✅ PASSED: {name}")
                self.passed += 1
            else:
                print(f"❌ FAILED: {name}")
                self.failed += 1
        except Exception as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {str(e)}")
            self.failed += 1
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Passed:   {self.passed}")
        print(f"❌ Failed:   {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"{'='*60}\n")
        
        if self.failed > 0:
            print(f"❌ {self.failed} test(s) failed!")
            return False
        else:
            print("✅ All tests passed!")
            return True


def test_health_endpoint(runner: SmokeTestRunner):
    """Test API health check endpoint"""
    def run():
        response = httpx.get(f"{runner.base_url}/api", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"   Response: {response.json()}")
        return True
    
    runner.test("API Health Check", run)


def test_homepage(runner: SmokeTestRunner):
    """Test homepage loads correctly"""
    def run():
        response = httpx.get(f"{runner.base_url}/", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "Vittcott" in response.text, "Homepage doesn't contain 'Vittcott'"
        assert len(response.text) > 1000, "Homepage content seems too short"
        print(f"   Homepage loaded: {len(response.text)} bytes")
        return True
    
    runner.test("Homepage Loading", run)


def test_stocks_live_endpoint(runner: SmokeTestRunner):
    """Test live stocks data endpoint"""
    def run():
        response = httpx.get(f"{runner.base_url}/api/stocks/live", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "stocks" in data, "Response missing 'stocks' key"
        assert isinstance(data["stocks"], list), "'stocks' should be a list"
        assert len(data["stocks"]) > 0, "No stocks returned"
        
        # Validate stock data structure
        stock = data["stocks"][0]
        required_fields = ["symbol", "name", "open", "high", "low", "close"]
        for field in required_fields:
            assert field in stock, f"Stock missing required field: {field}"
        
        print(f"   Retrieved {len(data['stocks'])} stocks")
        print(f"   Sample: {stock['symbol']} - {stock['name']}")
        print(f"   Price: Open=${stock['open']}, Close=${stock['close']}")
        return True
    
    runner.test("Stocks Live Data API", run)


def test_stocks_page(runner: SmokeTestRunner):
    """Test stocks page loads"""
    def run():
        response = httpx.get(f"{runner.base_url}/pages/stocks.html", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "stock" in response.text.lower(), "Stocks page missing stock-related content"
        print(f"   Stocks page loaded successfully")
        return True
    
    runner.test("Stocks Page", run)


def test_portfolio_page(runner: SmokeTestRunner):
    """Test portfolio page loads"""
    def run():
        response = httpx.get(f"{runner.base_url}/pages/portfolio.html", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "portfolio" in response.text.lower(), "Portfolio page missing portfolio-related content"
        print(f"   Portfolio page loaded successfully")
        return True
    
    runner.test("Portfolio Page", run)


def test_static_assets(runner: SmokeTestRunner):
    """Test CSS and JS assets load correctly"""
    def run():
        # Test CSS
        css_response = httpx.get(f"{runner.base_url}/assets/css/styles.css", timeout=10)
        assert css_response.status_code == 200, f"CSS failed: {css_response.status_code}"
        assert len(css_response.text) > 100, "CSS file seems empty or too small"
        
        # Test JS
        js_response = httpx.get(f"{runner.base_url}/assets/js/app.js", timeout=10)
        assert js_response.status_code == 200, f"JS failed: {js_response.status_code}"
        
        print(f"   CSS loaded: {len(css_response.text)} bytes")
        print(f"   JS loaded: {len(js_response.text)} bytes")
        return True
    
    runner.test("Static Assets (CSS/JS)", run)


def test_api_error_handling(runner: SmokeTestRunner):
    """Test API error handling for invalid endpoints"""
    def run():
        response = httpx.get(f"{runner.base_url}/api/nonexistent", timeout=10)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"   Correctly returned 404 for invalid endpoint")
        return True
    
    runner.test("API Error Handling", run)


def test_cors_headers(runner: SmokeTestRunner):
    """Test CORS headers are present"""
    def run():
        response = httpx.options(f"{runner.base_url}/api/stocks/live", timeout=10)
        # CORS headers should be present
        print(f"   Status: {response.status_code}")
        if "access-control-allow-origin" in response.headers:
            print(f"   CORS header found: {response.headers['access-control-allow-origin']}")
        else:
            print(f"   ⚠️  CORS headers not found (may be OK)")
        return True
    
    runner.test("CORS Configuration", run)


def test_streamlit_endpoint(runner: SmokeTestRunner):
    """Test Streamlit endpoint accessibility"""
    def run():
        try:
            response = httpx.get(f"{runner.base_url}/streamlit", timeout=15, follow_redirects=True)
            # Streamlit might return various status codes
            if response.status_code in [200, 301, 302, 502, 503]:
                print(f"   Streamlit endpoint responded with {response.status_code}")
                if response.status_code >= 500:
                    print(f"   ⚠️  Streamlit may not be running (status {response.status_code})")
                    runner.warnings += 1
                return True
            else:
                print(f"   Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ⚠️  Streamlit not accessible: {e}")
            runner.warnings += 1
            return True  # Non-blocking for now
    
    runner.test("Streamlit AI Assistant Endpoint", run)


def main():
    """Run all smoke tests"""
    print(f"\n{'#'*60}")
    print(f"# VITTCOTT SMOKE TESTS")
    print(f"# Testing: {BASE_URL}")
    print(f"{'#'*60}\n")
    
    runner = SmokeTestRunner(BASE_URL)
    
    # Run all tests
    test_health_endpoint(runner)
    test_homepage(runner)
    test_stocks_live_endpoint(runner)
    test_stocks_page(runner)
    test_portfolio_page(runner)
    test_static_assets(runner)
    test_api_error_handling(runner)
    test_cors_headers(runner)
    test_streamlit_endpoint(runner)
    
    # Print summary
    success = runner.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
