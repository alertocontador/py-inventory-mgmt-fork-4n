-- Inventory Management Database Schema

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- SKU table for inventory items
CREATE TABLE skus (
    sku_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku_code VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Temporary blocks table for inventory reservations
CREATE TABLE temporary_blocks (
    block_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku_id UUID NOT NULL REFERENCES skus(sku_id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    reason VARCHAR(500) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'converted', 'expired')),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP WITH TIME ZONE NULL,
    converted_at TIMESTAMP WITH TIME ZONE NULL
);

-- Indexes for performance optimization
CREATE INDEX idx_skus_sku_code ON skus(sku_code);
CREATE INDEX idx_skus_created_at ON skus(created_at);

CREATE INDEX idx_temporary_blocks_sku_id ON temporary_blocks(sku_id);
CREATE INDEX idx_temporary_blocks_status ON temporary_blocks(status);
CREATE INDEX idx_temporary_blocks_expires_at ON temporary_blocks(expires_at);
CREATE INDEX idx_temporary_blocks_created_at ON temporary_blocks(created_at);
