from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel

class ResponseClientMetadataDTO(BaseModel):
    client_ip: str = None
    client_type: Literal["stream-service", "user"]
    
class VideoFrameFromServiceDTO(BaseModel):
    frame_data: bytes
    
class CaptureStatusResponseDTO(BaseModel):
    rtsp_url: str
    is_active: bool