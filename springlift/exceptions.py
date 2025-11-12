from fastapi import HTTPException, status

class ScanNotFoundException(HTTPException):
    def __init__(self, scan_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID '{scan_id}' not found."
        )
