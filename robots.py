import io
import zipfile
from pathlib import Path
from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Robot, User
from app.schemas import RobotWithReports
from app.auth import get_current_user_from_bearer, ensure_user

router = APIRouter(
    prefix="/robots",
    tags=["robots"],
)

DATA_ROOT = Path("/home")


def get_authorized_robot(
    robot_folder: str,
    current_user: User = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
) -> Robot:
    """
    Vérifie que le robot existe et que l'utilisateur y a accès.
    Superuser peut accéder à tous les robots.
    """
    robot = db.query(Robot).filter_by(robot_folder=robot_folder).first()
    if not robot:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Robot introuvable")

    if current_user.role != "superuser" and not any(link.user_id == current_user.id for link in robot.users):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès interdit")

    return robot


@router.get(
    "/tree",
    response_model=List[RobotWithReports],
    dependencies=[Depends(ensure_user)]
)
def get_robots_tree(
    current_user: User = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
) -> List[RobotWithReports]:
    """
    Liste tous les fichiers de chaque robot.
    - superuser voit tous les robots.
    - user voit seulement les siens.
    """
    if current_user.role == "superuser":
        robots = db.query(Robot).all()
    else:
        robots = (
            db.query(Robot)
              .join(Robot.users)
              .filter_by(user_id=current_user.id)
              .all()
        )

    overview: List[RobotWithReports] = []
    for r in robots:
        folder = (DATA_ROOT / r.robot_folder / "DownloadUserData").resolve()
        files: List[str] = []
        if folder.is_dir():
            files = [f.name for f in folder.iterdir() if f.is_file()]
        overview.append(RobotWithReports(robot_folder=r.robot_folder, reports=files))
    return overview


@router.get(
    "/{robot_folder}/reports/all",
    dependencies=[Depends(ensure_user)]
)
def download_all_reports(
    robot: Robot = Depends(get_authorized_robot)
):
    """
    Télécharge tous les fichiers du robot sous forme d’archive ZIP.
    """
    folder = (DATA_ROOT / robot.robot_folder / "DownloadUserData").resolve()
    if not folder.is_dir():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dossier introuvable")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in folder.iterdir():
            if f.is_file():
                zf.write(f, arcname=f.name)
    buf.seek(0)

    zip_name = f"{robot.robot_folder}_reports.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_name}"}
    )


@router.get(
    "/{robot_folder}/reports",
    response_model=List[str],
    dependencies=[Depends(ensure_user)]
)
def list_robot_reports(
    robot: Robot = Depends(get_authorized_robot)
) -> List[str]:
    """
    Liste les fichiers disponibles pour un robot.
    """
    folder = (DATA_ROOT / robot.robot_folder / "DownloadUserData").resolve()
    if not folder.is_dir():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dossier introuvable")
    return [f.name for f in folder.iterdir() if f.is_file()]


@router.get(
    "/{robot_folder}/reports/{filename}",
    dependencies=[Depends(ensure_user)]
)
def download_robot_report(
    filename: str,
    robot: Robot = Depends(get_authorized_robot)
):
    """
    Télécharge un fichier individuel d’un robot.
    """
    file_path = (DATA_ROOT / robot.robot_folder / "DownloadUserData" / filename).resolve()
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fichier introuvable")
    if not str(file_path).startswith(str(DATA_ROOT)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Chemin de fichier invalide")
    return FileResponse(path=str(file_path), filename=filename)


@router.get("/status")
def get_robots_status(
    current_user: User = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    Renvoie l’état actif/inactif de chaque robot :
    - superuser et maintenance voient tous les robots.
    - user voit seulement ses robots.
    """
    if current_user.role in ("maintenance", "superuser"):
        robots = db.query(Robot).all()
    else:
        robots = (
            db.query(Robot)
              .join(Robot.users)
              .filter_by(user_id=current_user.id)
              .all()
        )

    now = datetime.now(timezone.utc)
    results = []
    for r in robots:
        script_file = DATA_ROOT / r.robot_folder / "script" / "last_seen.txt"
        if script_file.exists():
            mtime = datetime.fromtimestamp(script_file.stat().st_mtime, tz=timezone.utc)
            is_active = (now - mtime).total_seconds() < 300
            last_seen = mtime.isoformat()
        else:
            is_active = False
            last_seen = None

        results.append({
            "robot_folder": r.robot_folder,
            "is_active": is_active,
            "last_seen": last_seen
        })

    return JSONResponse(content=results)
