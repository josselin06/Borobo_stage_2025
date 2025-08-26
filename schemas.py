from typing import List

from pydantic import BaseModel


class LinkRobotRequest(BaseModel):
    robot_folder: str

class RobotResponse(BaseModel):
    id: int
    robot_folder: str

    class Config:
        from_attributes = True

class RobotWithReports(BaseModel):
    robot_folder: str
    reports: List[str]



