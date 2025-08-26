from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from decimal import Decimal
import uuid


class SkuCreateRequest(BaseModel):
    sku_code: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=500)
    quantity: int = Field(..., ge=0)
    price: Decimal = Field(..., gt=0, decimal_places=2)


class SkuResponse(BaseModel):
    sku_id: uuid.UUID
    sku_code: str
    name: str
    quantity: int
    price: Decimal
    created_at: datetime


class TemporaryBlockCreateRequest(BaseModel):
    quantity: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=500)
    expires_at: datetime


class TemporaryBlockResponse(BaseModel):
    block_id: uuid.UUID
    sku_id: uuid.UUID
    quantity: int
    reason: str
    status: str
    expires_at: datetime
    created_at: datetime


class TemporaryBlockWithSkuResponse(BaseModel):
    block_id: uuid.UUID
    sku_id: uuid.UUID
    sku_code: str
    quantity: int
    reason: str
    status: str
    expires_at: datetime
    created_at: datetime


class TemporaryBlocksListResponse(BaseModel):
    blocks: List[TemporaryBlockWithSkuResponse]
    total: int


class ConvertToPermanentRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


class ConvertToPermanentResponse(BaseModel):
    block_id: uuid.UUID
    status: str
    converted_at: datetime
    reason: str


class CancelBlockRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


class CancelBlockResponse(BaseModel):
    block_id: uuid.UUID
    status: str
    cancelled_at: datetime
    reason: str
