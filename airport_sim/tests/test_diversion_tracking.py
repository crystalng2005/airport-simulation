

import pytest
import sys
sys.path.insert(0, '..')

from logic.report import PerformanceReport


class TestReportInitialisation:
    """Test PerformanceReport object creation"""
    
    def test_report_created_with_defaults(self):
        """Test report initialises with default values"""
        report = PerformanceReport()
        assert report.diversions == 0
        assert report.cancellations == 0
        assert report.total_planes == 0


class TestDiversionTracking:
   
    
    def test_diversion_increment(self):
        """Test diversion count can be incremented"""
        report = PerformanceReport()
        report.diversions += 1
        assert report.diversions == 1
    
    def test_multiple_diversions_tracked(self):
        """Test multiple diversions are counted"""
        report = PerformanceReport()
        for i in range(5):
            report.diversions += 1
        assert report.diversions == 5


class TestCancellationTracking:
    
    
    def test_cancellation_increment(self):
        """Test cancellation count can be incremented"""
        report = PerformanceReport()
        report.cancellations += 1
        assert report.cancellations == 1


# Mark all tests
pytestmark = [pytest.mark.unit, pytest.mark.report]