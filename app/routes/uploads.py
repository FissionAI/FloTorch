import uuid
from typing import List
from pydantic import BaseModel
import logging

from http.client import HTTPException

from fastapi import APIRouter, Depends

from app.dependencies.s3 import get_s3_client, S3_BUCKET

logger = logging.getLogger(__name__)
router = APIRouter()

class PresignedurlRequestKB(BaseModel):
    unique_id: str
    files: List[str]
    
class PresignedurlRequestGT(BaseModel):
    unique_id: str
    
    
@router.post("/presignedurl", tags=["uploads"])
async def get_presigned_url(
    request: PresignedurlRequestGT, 
    s3=Depends(get_s3_client)
):
    unique_id = request.unique_id
    ground_truth_data_key = f"{unique_id}/gt_data/gt.json"

    gt_data_path = f"s3://{S3_BUCKET}/{ground_truth_data_key}"

    try:

        # Generate presigned URL for ground truth data upload
        gt_data_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": S3_BUCKET, "Key": ground_truth_data_key},
            ExpiresIn=7200,
        )
        logger.info(f"Generated presigned URL for ground truth data: {ground_truth_data_key}")

        return {
            "gt_data": {
                "path": gt_data_path,
                "presignedurl": gt_data_url
            },
            "uuid": unique_id,
        }
    except Exception as e:
        logger.error(f"Failed to generate presigned URL for ground truth data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating pre-signed URL: {str(e)}")

            
@router.post('/presigned_url_kb', tags = ['uploads'])
async def get_presigned_url_kb(
    request: PresignedurlRequestKB, 
    s3 = Depends(get_s3_client)
    ):
    
    try:
        unique_id = request.unique_id
        files = request.files
        
        prefix = f"{unique_id}/kb_data"
        
        # Check and clean existing files
        # TODO - optimize it by uploading only new files
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        if 'Contents' in response:
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            s3.delete_objects(Bucket=S3_BUCKET, Delete={'Objects': objects_to_delete})
            logger.info(f"Cleaned up existing files for KB upload: {prefix}")
            
        result = []
    
        # Generate presigned URLs for new files
        for file_name in files:
            file_key = f"{prefix}/{file_name}"
            file_path=f"s3://{S3_BUCKET}/{file_key}"
            
            data_url = s3.generate_presigned_url(
                    ClientMethod="put_object",
                    Params={"Bucket": S3_BUCKET, "Key": file_key},
                    ExpiresIn=7200,)
                
            result.append({
                "path": file_path,
                "presignedurl": data_url
                })
            
        logger.info(f"Generated {len(files)} presigned URLs for KB upload: {prefix}")
        return {'uuid': unique_id, "files": result}
      
    except Exception as e:
        logger.error(f"Failed to generate presigned URLs for KB upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating pre-signed URL: {str(e)}")