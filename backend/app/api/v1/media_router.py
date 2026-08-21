import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.api.deps import get_current_user
from app.modules.auth.models import User

router = APIRouter(prefix="/media", tags=["Media Upload"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload an image file and return its accessible URL."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ cho phép tải lên định dạng hình ảnh (JPG, PNG, WEBP, GIF)",
        )

    original_name = file.filename or "image.jpg"
    file_ext = Path(original_name).suffix.lower()
    if not file_ext or file_ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]:
        file_ext = ".jpg"

    unique_filename = f"{uuid.uuid4()}{file_ext}"
    target_path = UPLOAD_DIR / unique_filename

    try:
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lưu tệp tin: {str(e)}",
        )

    # Relative URL served by FastAPI static files mount
    file_url = f"/uploads/{unique_filename}"

    return {
        "url": file_url,
        "filename": original_name,
        "size": target_path.stat().st_size,
    }
