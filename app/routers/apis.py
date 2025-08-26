from fastapi import APIRouter, HTTPException
import uuid
from datetime import datetime
from db.postgresql import get_postgres_connection, get_postgres_cursor
from app.models import (
    SkuCreateRequest, SkuResponse,
    TemporaryBlockCreateRequest, TemporaryBlockResponse,
    TemporaryBlocksListResponse, TemporaryBlockWithSkuResponse,
    ConvertToPermanentRequest, ConvertToPermanentResponse,
    CancelBlockRequest, CancelBlockResponse
)

router = APIRouter()



@router.post("/sku", response_model=SkuResponse)
async def post_sku(request: SkuCreateRequest):
    connection = get_postgres_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = get_postgres_cursor(connection)
        
        # Check if SKU code already exists
        cursor.execute("SELECT sku_id FROM skus WHERE sku_code = %s", (request.sku_code,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"SKU code '{request.sku_code}' already exists")
        
        # Insert new SKU
        cursor.execute(
            """
            INSERT INTO skus (sku_code, name, quantity, price) 
            VALUES (%s, %s, %s, %s) 
            RETURNING sku_id, sku_code, name, quantity, price, created_at
            """,
            (request.sku_code, request.name, request.quantity, request.price)
        )
        
        result = cursor.fetchone()
        connection.commit()
        
        return SkuResponse(
            sku_id=result['sku_id'],
            sku_code=result['sku_code'],
            name=result['name'],
            quantity=result['quantity'],
            price=result['price'],
            created_at=result['created_at']
        )
        
    except HTTPException:
        connection.rollback()
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        connection.close()



@router.post("/sku/{sku_id}/temporary-block", response_model=TemporaryBlockResponse)
async def post_sku_sku_id_temporary_block(sku_id: uuid.UUID, request: TemporaryBlockCreateRequest):
    connection = get_postgres_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = get_postgres_cursor(connection)
        
        # Check if SKU exists and has sufficient quantity
        cursor.execute(
            "SELECT sku_code, quantity FROM skus WHERE sku_id = %s", 
            (str(sku_id),)
        )
        sku = cursor.fetchone()
        if not sku:
            raise HTTPException(status_code=404, detail="SKU not found")
        
        # Check available quantity (total - active blocks)
        cursor.execute(
            """
            SELECT COALESCE(SUM(quantity), 0) as blocked_quantity 
            FROM temporary_blocks 
            WHERE sku_id = %s AND status = 'active'
            """,
            (str(sku_id),)
        )
        blocked_result = cursor.fetchone()
        blocked_quantity = blocked_result['blocked_quantity'] if blocked_result else 0
        available_quantity = sku['quantity'] - blocked_quantity
        
        if available_quantity < request.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient inventory. Available: {available_quantity}, Requested: {request.quantity}"
            )
        
        # Create temporary block
        cursor.execute(
            """
            INSERT INTO temporary_blocks (sku_id, quantity, reason, expires_at) 
            VALUES (%s, %s, %s, %s) 
            RETURNING block_id, sku_id, quantity, reason, status, expires_at, created_at
            """,
            (str(sku_id), request.quantity, request.reason, request.expires_at)
        )
        
        result = cursor.fetchone()
        connection.commit()
        
        return TemporaryBlockResponse(
            block_id=result['block_id'],
            sku_id=result['sku_id'],
            quantity=result['quantity'],
            reason=result['reason'],
            status=result['status'],
            expires_at=result['expires_at'],
            created_at=result['created_at']
        )
        
    except HTTPException:
        connection.rollback()
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        connection.close()



@router.get("/temporary-blocks", response_model=TemporaryBlocksListResponse)
async def get_temporary_blocks():
    connection = get_postgres_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = get_postgres_cursor(connection)
        
        # Get all active temporary blocks with SKU info
        cursor.execute(
            """
            SELECT tb.block_id, tb.sku_id, s.sku_code, tb.quantity, 
                   tb.reason, tb.status, tb.expires_at, tb.created_at
            FROM temporary_blocks tb
            JOIN skus s ON tb.sku_id = s.sku_id
            WHERE tb.status = 'active'
            ORDER BY tb.created_at DESC
            """
        )
        
        results = cursor.fetchall()
        
        blocks = [
            TemporaryBlockWithSkuResponse(
                block_id=row['block_id'],
                sku_id=row['sku_id'],
                sku_code=row['sku_code'],
                quantity=row['quantity'],
                reason=row['reason'],
                status=row['status'],
                expires_at=row['expires_at'],
                created_at=row['created_at']
            )
            for row in results
        ]
        
        return TemporaryBlocksListResponse(
            blocks=blocks,
            total=len(blocks)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        connection.close()



@router.post("/temporary-blocks/{block_id}/convert-to-permanent", response_model=ConvertToPermanentResponse)
async def post_temporary_blocks_block_id_convert_to_permanent(block_id: uuid.UUID, request: ConvertToPermanentRequest):
    connection = get_postgres_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = get_postgres_cursor(connection)
        
        # Check if block exists and is active
        cursor.execute(
            "SELECT sku_id, quantity, status FROM temporary_blocks WHERE block_id = %s",
            (str(block_id),)
        )
        block = cursor.fetchone()
        
        if not block:
            raise HTTPException(status_code=404, detail="Temporary block not found")
        
        if block['status'] != 'active':
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot convert block with status '{block['status']}'. Only 'active' blocks can be converted."
            )
        
        # Update block status to converted
        converted_at = datetime.utcnow()
        cursor.execute(
            """
            UPDATE temporary_blocks 
            SET status = 'converted', converted_at = %s, updated_at = %s
            WHERE block_id = %s
            RETURNING block_id, status, converted_at
            """,
            (converted_at, converted_at, str(block_id))
        )
        
        result = cursor.fetchone()
        
        # Reduce SKU quantity permanently
        cursor.execute(
            "UPDATE skus SET quantity = quantity - %s, updated_at = %s WHERE sku_id = %s",
            (block['quantity'], converted_at, str(block['sku_id']))
        )
        
        connection.commit()
        
        return ConvertToPermanentResponse(
            block_id=result['block_id'],
            status=result['status'],
            converted_at=result['converted_at'],
            reason=request.reason
        )
        
    except HTTPException:
        connection.rollback()
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        connection.close()



@router.post("/temporary-blocks/{block_id}/cancel", response_model=CancelBlockResponse)
async def post_temporary_blocks_block_id_cancel(block_id: uuid.UUID, request: CancelBlockRequest):
    connection = get_postgres_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = get_postgres_cursor(connection)
        
        # Check if block exists and is active
        cursor.execute(
            "SELECT status FROM temporary_blocks WHERE block_id = %s",
            (str(block_id),)
        )
        block = cursor.fetchone()
        
        if not block:
            raise HTTPException(status_code=404, detail="Temporary block not found")
        
        if block['status'] != 'active':
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel block with status '{block['status']}'. Only 'active' blocks can be cancelled."
            )
        
        # Update block status to cancelled
        cancelled_at = datetime.utcnow()
        cursor.execute(
            """
            UPDATE temporary_blocks 
            SET status = 'cancelled', cancelled_at = %s, updated_at = %s
            WHERE block_id = %s
            RETURNING block_id, status, cancelled_at
            """,
            (cancelled_at, cancelled_at, str(block_id))
        )
        
        result = cursor.fetchone()
        connection.commit()
        
        return CancelBlockResponse(
            block_id=result['block_id'],
            status=result['status'],
            cancelled_at=result['cancelled_at'],
            reason=request.reason
        )
        
    except HTTPException:
        connection.rollback()
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

