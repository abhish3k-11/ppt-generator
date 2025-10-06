-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas for organization
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS presentations;
CREATE SCHEMA IF NOT EXISTS tasks;
CREATE SCHEMA IF NOT EXISTS files;

-- Create users table
CREATE TABLE users.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create presentations table
CREATE TABLE presentations.presentations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    content JSONB,
    slides JSONB,
    theme VARCHAR(50) DEFAULT 'professional',
    slide_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'draft', -- draft, generating, completed, failed
    user_id UUID REFERENCES users.users(id) ON DELETE CASCADE,
    original_file_path VARCHAR(1000),
    export_formats JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create tasks table for background processing
CREATE TABLE tasks.processing_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_type VARCHAR(100) NOT NULL, -- document_processing, ai_generation, presentation_rendering
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed, cancelled
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    input_data JSONB NOT NULL,
    result_data JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    user_id UUID REFERENCES users.users(id) ON DELETE CASCADE,
    presentation_id UUID REFERENCES presentations.presentations(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create files table for uploaded documents
CREATE TABLE files.uploaded_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_filename VARCHAR(500) NOT NULL,
    stored_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(200),
    file_hash VARCHAR(64),
    upload_status VARCHAR(50) DEFAULT 'uploaded',
    user_id UUID REFERENCES users.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_presentations_user_id ON presentations.presentations(user_id);
CREATE INDEX idx_presentations_status ON presentations.presentations(status);
CREATE INDEX idx_presentations_created_at ON presentations.presentations(created_at);
CREATE INDEX idx_tasks_status ON tasks.processing_tasks(status);
CREATE INDEX idx_tasks_task_type ON tasks.processing_tasks(task_type);
CREATE INDEX idx_tasks_user_id ON tasks.processing_tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks.processing_tasks(created_at);
CREATE INDEX idx_files_user_id ON files.uploaded_files(user_id);
CREATE INDEX idx_files_file_hash ON files.uploaded_files(file_hash);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_presentations_updated_at BEFORE UPDATE ON presentations.presentations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks.processing_tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for development
INSERT INTO users.users (email, username, password_hash, first_name, last_name) VALUES 
('admin@pptgen.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewfBmdlyxXZz5s8m', 'Admin', 'User'),
('test@pptgen.com', 'testuser', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewfBmdlyxXZz5s8m', 'Test', 'User');

-- Grant permissions (optional - for production you'd want more specific permissions)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA users TO ppt_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA presentations TO ppt_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA tasks TO ppt_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA files TO ppt_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA users TO ppt_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA presentations TO ppt_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA tasks TO ppt_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA files TO ppt_admin;

-- Show summary
SELECT 'Database initialization completed!' as status;
SELECT schemaname, tablename FROM pg_tables WHERE schemaname IN ('users', 'presentations', 'tasks', 'files') ORDER BY schemaname, tablename;
