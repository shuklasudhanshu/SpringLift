from typing import Dict
from .models import ScanResult

# In-memory storage for scan results
_scan_results: Dict[str, ScanResult] = {}

def save_scan_result(result: ScanResult):
    _scan_results[result.id] = result

def get_scan_result(scan_id: str) -> ScanResult:
    return _scan_results.get(scan_id)

def clear_storage():
    _scan_results.clear()
