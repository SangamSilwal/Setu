-- ============================================================
-- SETU - Chat Persistence Schema
-- ============================================================
-- Description: Creates tables for storing chat conversations and messages
-- Author: Development Team
-- Date: 2026-01-05
-- Version: 1.0
-- ============================================================

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- Table: chat_conversations
-- ============================================================
-- Stores conversation metadata for each user's chat session
-- Each conversation belongs to one user from auth.users

CREATE TABLE IF NOT EXISTS public.chat_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE public.chat_conversations IS 'Stores chat conversation metadata for users';
COMMENT ON COLUMN public.chat_conversations.id IS 'Unique conversation identifier';
COMMENT ON COLUMN public.chat_conversations.user_id IS 'References the user who owns this conversation (from auth.users)';
COMMENT ON COLUMN public.chat_conversations.title IS 'Conversation title, typically derived from first message';
COMMENT ON COLUMN public.chat_conversations.created_at IS 'Timestamp when conversation was created';
COMMENT ON COLUMN public.chat_conversations.updated_at IS 'Timestamp when conversation was last updated';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_chat_conversations_user_id
    ON public.chat_conversations(user_id);

CREATE INDEX IF NOT EXISTS idx_chat_conversations_created_at
    ON public.chat_conversations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_conversations_updated_at
    ON public.chat_conversations(updated_at DESC);

-- ============================================================
-- Table: chat_messages
-- ============================================================
-- Stores individual messages within conversations
-- Each message belongs to one conversation

CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES public.chat_conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT NULL
);

-- Add comments for documentation
COMMENT ON TABLE public.chat_messages IS 'Stores individual messages within chat conversations';
COMMENT ON COLUMN public.chat_messages.id IS 'Unique message identifier';
COMMENT ON COLUMN public.chat_messages.conversation_id IS 'References the conversation this message belongs to';
COMMENT ON COLUMN public.chat_messages.role IS 'Message sender: "user" or "assistant"';
COMMENT ON COLUMN public.chat_messages.content IS 'Message content (text)';
COMMENT ON COLUMN public.chat_messages.timestamp IS 'Timestamp when message was created';
COMMENT ON COLUMN public.chat_messages.metadata IS 'Optional JSON metadata (e.g., sources, tokens, model info)';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id
    ON public.chat_messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp
    ON public.chat_messages(timestamp ASC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_role
    ON public.chat_messages(role);

-- ============================================================
-- Function: Update updated_at timestamp automatically
-- ============================================================
-- Automatically updates the updated_at column when a conversation is modified

CREATE OR REPLACE FUNCTION public.update_conversation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.chat_conversations
    SET updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update conversation timestamp when new message is added
DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON public.chat_messages;
CREATE TRIGGER trigger_update_conversation_timestamp
    AFTER INSERT ON public.chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION public.update_conversation_updated_at();

-- ============================================================
-- Row Level Security (RLS) Policies
-- ============================================================
-- Ensures users can only access their own conversations and messages

-- Enable RLS on both tables
ALTER TABLE public.chat_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for re-running migration)
DROP POLICY IF EXISTS "Users can view their own conversations" ON public.chat_conversations;
DROP POLICY IF EXISTS "Users can insert their own conversations" ON public.chat_conversations;
DROP POLICY IF EXISTS "Users can update their own conversations" ON public.chat_conversations;
DROP POLICY IF EXISTS "Users can delete their own conversations" ON public.chat_conversations;

DROP POLICY IF EXISTS "Users can view messages in their conversations" ON public.chat_messages;
DROP POLICY IF EXISTS "Users can insert messages in their conversations" ON public.chat_messages;
DROP POLICY IF EXISTS "Users can delete messages in their conversations" ON public.chat_messages;

-- Conversation Policies
CREATE POLICY "Users can view their own conversations"
    ON public.chat_conversations
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own conversations"
    ON public.chat_conversations
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own conversations"
    ON public.chat_conversations
    FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own conversations"
    ON public.chat_conversations
    FOR DELETE
    USING (auth.uid() = user_id);

-- Message Policies (messages can only be accessed through owned conversations)
CREATE POLICY "Users can view messages in their conversations"
    ON public.chat_messages
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.chat_conversations
            WHERE chat_conversations.id = chat_messages.conversation_id
            AND chat_conversations.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert messages in their conversations"
    ON public.chat_messages
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.chat_conversations
            WHERE chat_conversations.id = chat_messages.conversation_id
            AND chat_conversations.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete messages in their conversations"
    ON public.chat_messages
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.chat_conversations
            WHERE chat_conversations.id = chat_messages.conversation_id
            AND chat_conversations.user_id = auth.uid()
        )
    );

-- ============================================================
-- Grant permissions to authenticated users
-- ============================================================

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON public.chat_conversations TO authenticated;
GRANT ALL ON public.chat_messages TO authenticated;

-- ============================================================
-- Sample Data (Optional - Comment out if not needed)
-- ============================================================

-- Uncomment below to insert sample data for testing
-- Note: Replace 'your-user-id-here' with an actual user ID from auth.users

/*
-- Insert sample conversation
INSERT INTO public.chat_conversations (user_id, title)
VALUES ('your-user-id-here', 'Sample Legal Query');

-- Get the conversation ID (replace with actual ID after insert)
-- INSERT INTO public.chat_messages (conversation_id, role, content)
-- VALUES
--     ('conversation-id-here', 'user', 'What are my property rights in Nepal?'),
--     ('conversation-id-here', 'assistant', 'In Nepal, property rights are governed by...');
*/

-- ============================================================
-- Verification Queries (Run these to verify setup)
-- ============================================================

-- Check if tables were created
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public' AND table_name IN ('chat_conversations', 'chat_messages');

-- Check if indexes were created
-- SELECT indexname FROM pg_indexes
-- WHERE tablename IN ('chat_conversations', 'chat_messages');

-- Check if RLS is enabled
-- SELECT tablename, rowsecurity FROM pg_tables
-- WHERE schemaname = 'public' AND tablename IN ('chat_conversations', 'chat_messages');

-- ============================================================
-- Migration Complete!
-- ============================================================
-- Next Steps:
-- 1. Run this SQL in your Supabase SQL Editor
-- 2. Verify tables are created in the Table Editor
-- 3. Test with backend API routes
-- ============================================================
