import sys
import os
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Ensure parent repo is in path for Sports2D import
sys.path.insert(0, "/app/Sports2D-Web")

from celery import shared_task
from app.config import settings
from app.models import JobStatus
from app.services.storage import SessionLocal, JobRecord, storage_service
from app.services.video_processor import create_segments, get_video_duration

logger = logging.getLogger(__name__)

def build_sports2d_config(params: dict, video_files: list, video_dir: str, result_dir: str, time_ranges: list = None):
    """Build a Sports2D-compatible nested config dict from flat web params."""
    
    # Import default config structure
    from Sports2D.Sports2D import DEFAULT_CONFIG
    import copy
    config = copy.deepcopy(DEFAULT_CONFIG)
    
    # Base settings
    config["base"]["video_input"] = video_files
    config["base"]["video_dir"] = video_dir
    config["base"]["result_dir"] = result_dir
    config["base"]["show_realtime_results"] = False
    config["base"]["save_vid"] = True
    config["base"]["save_img"] = True
    config["base"]["save_pose"] = True
    config["base"]["calculate_angles"] = True
    config["base"]["save_angles"] = True
    config["base"]["time_range"] = time_ranges if time_ranges else []
    
    # Override with user params
    base_keys = ["nb_persons_to_detect", "person_ordering_method", "first_person_height", "visible_side"]
    for k in base_keys:
        if k in params:
            config["base"][k] = params[k]
    
    # Ensure headless-safe ordering
    if config["base"].get("person_ordering_method") == "on_click":
        config["base"]["person_ordering_method"] = "highest_likelihood"
    
    # Pose
    pose_keys = ["slowmo_factor", "pose_model", "mode", "det_frequency", "device", "backend", 
                 "tracking_mode", "keypoint_likelihood_threshold", "average_likelihood_threshold",
                 "keypoint_number_threshold", "max_distance", "max_unseen_time"]
    for k in pose_keys:
        if k in params:
            config["pose"][k] = params[k]
    
    # Angles
    angle_keys = ["joint_angles", "segment_angles", "correct_segment_angles_with_floor_angle", "fontSize"]
    for k in angle_keys:
        if k in params:
            config["angles"][k] = params[k]
    display = params.get("display_angle_values_on", ["body", "list"])
    config["angles"]["display_angle_values_on"] = display
    
    # Meters conversion
    px_keys = ["to_meters", "make_c3d", "floor_angle", "xy_origin", "perspective_value", 
               "perspective_unit", "distortions", "calib_file"]
    for k in px_keys:
        if k in params:
            config["px_to_meters_conversion"][k] = params[k]
    config["px_to_meters_conversion"]["save_calib"] = True
    
    # Post-processing
    pp_keys = ["interpolate", "interp_gap_smaller_than", "fill_large_gaps_with", 
               "sections_to_keep", "min_chunk_size", "reject_outliers", "filter", 
               "show_graphs", "save_graphs", "filter_type"]
    for k in pp_keys:
        if k in params:
            config["post-processing"][k] = params[k]
    
    config["post-processing"]["show_graphs"] = False  # headless
    
    # Filter-specific params
    if params.get("filter_type") == "butterworth":
        config["post-processing"]["butterworth"]["cut_off_frequency"] = params.get("butterworth_cut_off_frequency", 6.0)
        config["post-processing"]["butterworth"]["order"] = params.get("butterworth_order", 4)
    
    # Kinematics
    kin_keys = ["do_augmentation", "do_ik", "filter_ik", "ik_filter_type", "feet_on_floor",
                "use_simple_model", "participant_mass", "right_left_symmetry", "default_height",
                "large_hip_knee_angles", "trimmed_extrema_percent", "remove_individual_scaling_setup",
                "remove_individual_ik_setup", "parallel_workers_kinematics"]
    for k in kin_keys:
        if k in params:
            config["kinematics"][k] = params[k]
    
    config["logging"]["use_custom_logging"] = True
    
    return config

def update_job_status(job_id: str, status: str, progress: int = None, message: str = None, result_path: str = None, size_mb: float = None):
    db = SessionLocal()
    try:
        job = db.query(JobRecord).filter(JobRecord.job_id == job_id).first()
        if job:
            job.status = status
            if progress is not None:
                job.progress_percent = progress
            if message is not None:
                job.message = message
            if result_path is not None:
                job.result_path = result_path
            if size_mb is not None:
                job.result_size_mb = size_mb
            if status == JobStatus.COMPLETED.value:
                job.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        logger.error(f"DB update failed for {job_id}: {e}")
    finally:
        db.close()

@shared_task(bind=True, max_retries=1)
def process_video_task(self, job_id: str, segments: list, params: dict, expert_mode: bool):
    logger.info(f"Starting processing for job {job_id}")
    update_job_status(job_id, JobStatus.PROCESSING.value, progress=5, message="Preparing video segments")
    
    try:
        db = SessionLocal()
        job = db.query(JobRecord).filter(JobRecord.job_id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        original_path = Path(job.upload_path)
        db.close()
        
        upload_dir = storage_service.get_job_upload_dir(job_id)
        result_dir = storage_service.get_job_result_dir(job_id)
        
        # Determine video files to process
        video_files = []
        if segments:
            update_job_status(job_id, JobStatus.PROCESSING.value, progress=10, message="Trimming video segments")
            seg_paths = create_segments(original_path, upload_dir / "segments", segments)
            video_files = [p.name for p in seg_paths]
            video_dir = str(seg_paths[0].parent)
            time_ranges = []
        else:
            video_files = [original_path.name]
            video_dir = str(original_path.parent)
            time_ranges = []
        
        update_job_status(job_id, JobStatus.PROCESSING.value, progress=20, message="Running Sports2D analysis")
        
        # Build config
        config = build_sports2d_config(params, video_files, video_dir, str(result_dir), time_ranges)
        
        # Run Sports2D
        import warnings
        warnings.filterwarnings("ignore")
        
        # Set matplotlib backend to Agg before importing pyplot
        import matplotlib
        matplotlib.use('Agg')
        
        from Sports2D import Sports2D
        Sports2D.process(config)
        
        update_job_status(job_id, JobStatus.PROCESSING.value, progress=80, message="Packaging results")
        
        # Create ZIP
        zip_result = storage_service.create_result_zip(job_id)
        if zip_result:
            zip_path, size_mb = zip_result
            update_job_status(job_id, JobStatus.COMPLETED.value, progress=100, 
                            message="Analysis complete. Ready for download.",
                            result_path=str(zip_path), size_mb=size_mb)
        else:
            update_job_status(job_id, JobStatus.FAILED.value, message="No results generated")
        
    except Exception as e:
        logger.error(f"Processing failed for {job_id}: {e}\n{traceback.format_exc()}")
        update_job_status(job_id, JobStatus.FAILED.value, message=f"Error: {str(e)}")

@shared_task
def delete_job_files_task(job_id: str):
    """Delete job files immediately after download."""
    logger.info(f"Deleting files for job {job_id}")
    storage_service.delete_job_files(job_id)
    db = SessionLocal()
    try:
        job = db.query(JobRecord).filter(JobRecord.job_id == job_id).first()
        if job:
            job.deleted = "true"
            db.commit()
    finally:
        db.close()

@shared_task
def cleanup_old_jobs_task():
    """Periodic cleanup of old jobs."""
    from app.services.storage import cleanup_old_jobs
    cleanup_old_jobs()
