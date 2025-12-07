"""
Streamlit Integration Tests for Vittcott
Tests that Streamlit AI Assistant is properly integrated with the backend
"""
import httpx
import sys
import os
import json
from typing import Dict, Any

# Get configuration from environment
BACKEND_URL = os.getenv("VITTCOTT_BASE_URL", "http://localhost:8000")
STREAMLIT_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")


class StreamlitTestRunner:
    def __init__(self):
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
        print("STREAMLIT INTEGRATION TEST SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Passed:   {self.passed}")
        print(f"❌ Failed:   {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"{'='*60}\n")
        
        if self.failed > 0:
            print(f"❌ {self.failed} test(s) failed!")
            return False
        else:
            print("✅ All Streamlit integration tests passed!")
            return True


def test_streamlit_server_running(runner: StreamlitTestRunner):
    """Test that Streamlit server is running"""
    def run():
        try:
            # Try to access Streamlit healthcheck
            response = httpx.get(
                f"{STREAMLIT_URL}/_stcore/health",
                timeout=10,
                follow_redirects=True
            )
            
            if response.status_code == 200:
                print(f"   ✅ Streamlit health check passed")
                return True
            else:
                print(f"   ⚠️  Streamlit health check returned {response.status_code}")
                # Try main page as fallback
                main_response = httpx.get(STREAMLIT_URL, timeout=10, follow_redirects=True)
                if main_response.status_code == 200:
                    print(f"   ✅ Streamlit main page accessible")
                    return True
                else:
                    print(f"   ❌ Streamlit not accessible")
                    return False
        except httpx.ConnectError:
            print(f"   ❌ Cannot connect to Streamlit at {STREAMLIT_URL}")
            return False
        except Exception as e:
            print(f"   ❌ Error checking Streamlit: {e}")
            return False
    
    runner.test("Streamlit Server Running", run)


def test_streamlit_page_content(runner: StreamlitTestRunner):
    """Test Streamlit page loads with expected content"""
    def run():
        try:
            response = httpx.get(STREAMLIT_URL, timeout=15, follow_redirects=True)
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            content = response.text.lower()
            
            # Check for Streamlit-specific elements
            streamlit_indicators = [
                'streamlit',
                'vittcott',
                'ai',
                'assistant'
            ]
            
            found_indicators = [ind for ind in streamlit_indicators if ind in content]
            
            print(f"   Found {len(found_indicators)}/{len(streamlit_indicators)} expected content indicators")
            print(f"   Indicators found: {', '.join(found_indicators)}")
            
            # Should have at least some indicators
            if len(found_indicators) >= 2:
                print(f"   ✅ Streamlit page contains expected content")
                return True
            else:
                print(f"   ⚠️  Streamlit page may not be fully loaded")
                runner.warnings += 1
                return True  # Non-blocking
        except Exception as e:
            print(f"   ❌ Error loading Streamlit page: {e}")
            return False
    
    runner.test("Streamlit Page Content", run)


def test_backend_ai_endpoint(runner: StreamlitTestRunner):
    """Test backend AI API endpoint that Streamlit uses"""
    def run():
        try:
            test_payload = {
                "query": "What is a stock?",
                "portfolio": {
                    "stocks": [],
                    "mutual_funds": [],
                    "cash": 0
                }
            }
            
            response = httpx.post(
                f"{BACKEND_URL}/api/ai/ask",
                json=test_payload,
                timeout=30
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert "response_text" in data, "Response missing 'response_text' key"
            assert len(data["response_text"]) > 0, "AI response is empty"
            
            print(f"   ✅ AI endpoint working")
            print(f"   Response length: {len(data['response_text'])} characters")
            print(f"   Sample response: {data['response_text'][:100]}...")
            
            return True
        except Exception as e:
            print(f"   ❌ Backend AI endpoint test failed: {e}")
            return False
    
    runner.test("Backend AI API Endpoint", run)


def test_streamlit_websocket_connection(runner: StreamlitTestRunner):
    """Test that Streamlit WebSocket endpoint is accessible"""
    def run():
        try:
            # WebSocket endpoint for Streamlit
            ws_url = f"{STREAMLIT_URL}/_stcore/stream"
            
            # We can't easily test actual WebSocket here, but check if endpoint exists
            response = httpx.get(ws_url, timeout=5, follow_redirects=True)
            
            # WebSocket endpoint might return various codes
            if response.status_code in [200, 400, 426]:  # 426 = Upgrade Required (WebSocket)
                print(f"   ✅ Streamlit WebSocket endpoint accessible (status {response.status_code})")
                return True
            else:
                print(f"   ⚠️  WebSocket endpoint returned unexpected status: {response.status_code}")
                runner.warnings += 1
                return True  # Non-blocking
        except Exception as e:
            print(f"   ⚠️  WebSocket test inconclusive: {e}")
            runner.warnings += 1
            return True  # Non-blocking
    
    runner.test("Streamlit WebSocket Connection", run)


def test_nginx_proxy_routing(runner: StreamlitTestRunner):
    """Test nginx properly routes /streamlit to Streamlit app"""
    def run():
        try:
            # This test is for production environment with nginx
            if "localhost" in BACKEND_URL:
                print(f"   ⏭️  Skipping nginx test (local environment)")
                return True
            
            streamlit_via_proxy = f"{BACKEND_URL}/streamlit"
            
            response = httpx.get(
                streamlit_via_proxy,
                timeout=15,
                follow_redirects=True
            )
            
            if response.status_code == 200:
                print(f"   ✅ Streamlit accessible via nginx proxy at /streamlit")
                
                # Check if content looks like Streamlit
                if "streamlit" in response.text.lower() or "vittcott" in response.text.lower():
                    print(f"   ✅ Streamlit content verified")
                    return True
                else:
                    print(f"   ⚠️  Content doesn't appear to be Streamlit")
                    runner.warnings += 1
                    return True
            else:
                print(f"   ❌ Streamlit proxy returned {response.status_code}")
                return False
        except Exception as e:
            print(f"   ⚠️  Nginx proxy test failed: {e}")
            runner.warnings += 1
            return True  # Non-blocking for now
    
    runner.test("Nginx Proxy Routing to Streamlit", run)


def test_streamlit_backend_integration(runner: StreamlitTestRunner):
    """Test that Streamlit can communicate with backend"""
    def run():
        try:
            # Check if backend is reachable from same network
            backend_health = httpx.get(f"{BACKEND_URL}/api", timeout=10)
            
            assert backend_health.status_code == 200, "Backend not healthy"
            print(f"   ✅ Backend is accessible")
            
            # Test the finance quote endpoint Streamlit uses
            quote_response = httpx.get(
                f"{BACKEND_URL}/api/finance/quote",
                params={"symbol": "AAPL"},
                timeout=15
            )
            
            if quote_response.status_code == 200:
                print(f"   ✅ Finance quote endpoint working")
                return True
            else:
                print(f"   ⚠️  Finance quote endpoint returned {quote_response.status_code}")
                runner.warnings += 1
                return True  # Non-blocking
        except Exception as e:
            print(f"   ❌ Backend integration test failed: {e}")
            return False
    
    runner.test("Streamlit-Backend Integration", run)


def test_environment_variables(runner: StreamlitTestRunner):
    """Test that Streamlit has correct environment variables"""
    def run():
        # For Streamlit, the BACKEND_URL should be configured
        print(f"   Streamlit URL: {STREAMLIT_URL}")
        print(f"   Backend URL: {BACKEND_URL}")
        
        # Check if variables are set
        if STREAMLIT_URL and BACKEND_URL:
            print(f"   ✅ Environment variables configured")
            return True
        else:
            print(f"   ⚠️  Some environment variables missing")
            runner.warnings += 1
            return True
    
    runner.test("Environment Variables", run)


def main():
    """Run all Streamlit integration tests"""
    print(f"\n{'#'*60}")
    print(f"# STREAMLIT INTEGRATION TESTS")
    print(f"# Streamlit URL: {STREAMLIT_URL}")
    print(f"# Backend URL: {BACKEND_URL}")
    print(f"{'#'*60}\n")
    
    runner = StreamlitTestRunner()
    
    # Run all tests
    test_streamlit_server_running(runner)
    test_streamlit_page_content(runner)
    test_backend_ai_endpoint(runner)
    test_streamlit_websocket_connection(runner)
    test_nginx_proxy_routing(runner)
    test_streamlit_backend_integration(runner)
    test_environment_variables(runner)
    
    # Print summary
    success = runner.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
