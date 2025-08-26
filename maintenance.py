from pathlib import Path
from typing import List
import io
import zipfile

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Robot, User
from app.auth import get_current_user_from_bearer, ensure_maintenance
from app.schemas import RobotWithReports

router = APIRouter(
    prefix="/maintenance",
    tags=["maintenance"],
    dependencies=[Depends(ensure_maintenance)]  
)

DATA_ROOT = Path("/home")

def get_maintainer(current_user: User = Depends(get_current_user_from_bearer)) -> User:
    return current_user 

@router.get("/reports", response_model=List[RobotWithReports])
def all_reports(
    _: User = Depends(get_maintainer),
    db: Session = Depends(get_db)
) -> List[RobotWithReports]:
    """
    Liste tous les fichiers de maintenance pour chaque robot.
    """
    robots = db.query(Robot).all()
    overview: List[RobotWithReports] = []

    for r in robots:
        folder = (DATA_ROOT / r.robot_folder / "maintenance").resolve()

        if not folder.exists():
            files = []
        elif not folder.is_dir():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chemin inattendu pour {r.robot_folder}/maintenance"
            )
        else:
            files = [f.name for f in folder.iterdir() if f.is_file()]

        overview.append(RobotWithReports(robot_folder=r.robot_folder, reports=files))

    return overview

@router.get("/download")
def download_maintenance_file(
    robot_folder: str = Query(...),
    filename: str = Query(...),
    _: User = Depends(get_maintainer),
):
    """
    Télécharge un fichier de maintenance unique.
    """
    expected_dir = (DATA_ROOT / robot_folder / "maintenance").resolve()
    file_path = (expected_dir / filename).resolve()

    if not file_path.exists() or not file_path.is_file() or expected_dir not in file_path.parents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier introuvable")

    return FileResponse(path=str(file_path), filename=filename, media_type="application/octet-stream")

@router.get("/{robot_folder}/reports/all")
def download_all_maintenance_reports(
    robot_folder: str,
    _: User = Depends(get_maintainer),
):
    """
    Télécharge tous les fichiers de maintenance d’un robot sous forme de ZIP.
    """
    folder = (DATA_ROOT / robot_folder / "maintenance").resolve()
    if not folder.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dossier introuvable")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in folder.iterdir():
            if f.is_file():
                zf.write(f, arcname=f.name)
    buf.seek(0)

    zip_name = f"{robot_folder}_maintenance_reports.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_name}"}
    )
