from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PREPROCESSING = "preprocessing"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Segment(BaseModel):
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., ge=0, description="End time in seconds")

class Sports2DParams(BaseModel):
    # Base params visible in standard mode
    nb_persons_to_detect: Union[int, str] = "all"
    person_ordering_method: str = "on_click"
    first_person_height: float = 1.65
    visible_side: List[str] = ["auto", "front", "none"]
    
    # Expert params
    pose_model: str = "Body_with_feet"
    mode: str = "balanced"
    det_frequency: int = 4
    device: str = "auto"
    backend: str = "auto"
    tracking_mode: str = "sports2d"
    keypoint_likelihood_threshold: float = 0.3
    average_likelihood_threshold: float = 0.5
    keypoint_number_threshold: float = 0.3
    max_distance: int = 250
    max_unseen_time: float = 1.0
    
    # Post-processing
    interpolate: bool = True
    interp_gap_smaller_than: int = 100
    fill_large_gaps_with: str = "last_value"
    sections_to_keep: str = "all"
    min_chunk_size: int = 10
    reject_outliers: bool = True
    filter: bool = True
    filter_type: str = "butterworth"
    butterworth_cut_off_frequency: float = 6.0
    butterworth_order: int = 4
    
    # Angles
    joint_angles: List[str] = [
        "Right ankle", "Left ankle", "Right knee", "Left knee",
        "Right hip", "Left hip", "Right shoulder", "Left shoulder",
        "Right elbow", "Left elbow", "Right wrist", "Left wrist"
    ]
    segment_angles: List[str] = [
        "Right foot", "Left foot", "Right shank", "Left shank",
        "Right thigh", "Left thigh", "Pelvis", "Trunk",
        "Shoulders", "Head", "Right arm", "Left arm",
        "Right forearm", "Left forearm"
    ]
    correct_segment_angles_with_floor_angle: bool = True
    
    # Kinematics
    do_ik: bool = False
    filter_ik: bool = False
    ik_filter_type: str = "acc_minimizing"
    feet_on_floor: bool = False
    use_simple_model: bool = False
    participant_mass: List[float] = [70.0]
    
    # Meters conversion
    to_meters: bool = True
    make_c3d: bool = True
    floor_angle: Union[float, str] = "auto"
    xy_origin: List[Union[float, str]] = ["auto"]
    perspective_value: float = 10.0
    perspective_unit: str = "distance_m"
    
    class Config:
        json_schema_extra = {
            "example": {
                "nb_persons_to_detect": "all",
                "person_ordering_method": "on_click",
                "first_person_height": 1.65,
                "visible_side": ["auto", "front", "none"],
                "pose_model": "Body_with_feet",
                "mode": "balanced",
                "det_frequency": 4,
                "device": "auto",
                "backend": "auto",
            }
        }

class VideoUploadResponse(BaseModel):
    job_id: str
    preview_url: str
    original_duration: float
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percent: int = 0
    message: Optional[str] = None
    download_url: Optional[str] = None
    result_size_mb: Optional[float] = None

class ProcessRequest(BaseModel):
    job_id: str
    segments: List[Segment] = []
    params: Sports2DParams = Field(default_factory=Sports2DParams)
    expert_mode: bool = False
