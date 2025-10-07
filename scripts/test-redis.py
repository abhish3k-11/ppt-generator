import redis
import json
import time
import threading
from datetime import datetime

def test_redis_connection():
    """Test basic Redis connectivity and operations"""
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Test connection
        r.ping()
        print("✅ Redis connection successful!")
        
        # Test basic operations
        r.set('test:connection', 'PPT Generator Redis Test')
        value = r.get('test:connection')
        print(f"✅ Basic operations work: {value}")
        
        # Test expiration
        r.setex('test:expire', 5, 'This will expire in 5 seconds')
        print("✅ Expiration set successfully")
        
        # Test hash operations (for caching structured data)
        task_data = {
            'task_id': 'task_123',
            'status': 'processing',
            'progress': 50,
            'created_at': datetime.now().isoformat()
        }
        r.hset('tasks:task_123', mapping=task_data)
        cached_task = r.hgetall('tasks:task_123')
        print(f"✅ Hash operations work: {cached_task}")
        
        # Test list operations (for task queues)
        r.lpush('task:queue', 'document_processing_task_1')
        r.lpush('task:queue', 'ai_generation_task_2')
        queue_length = r.llen('task:queue')
        print(f"✅ Queue operations work: {queue_length} tasks in queue")
        
        # Test pub/sub (for microservices communication)
        print("✅ Testing pub/sub...")
        test_pubsub(r)
        
        print("🎉 All Redis tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

def test_pubsub(redis_client):
    """Test Redis pub/sub functionality"""
    
    def subscriber():
        """Subscriber function"""
        pubsub = redis_client.pubsub()
        pubsub.subscribe('presentation.events')
        
        print("📡 Subscriber listening for messages...")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                print(f"📨 Received: {data}")
                break
        
        pubsub.close()
    
    # Start subscriber in background
    subscriber_thread = threading.Thread(target=subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()
    
    # Give subscriber time to connect
    time.sleep(1)
    
    # Publish a test message
    test_message = {
        'event': 'presentation.created',
        'task_id': 'task_456',
        'timestamp': datetime.now().isoformat()
    }
    
    redis_client.publish('presentation.events', json.dumps(test_message))
    print("📤 Published test message")
    
    # Wait for message processing
    time.sleep(1)

def test_caching_patterns():
    """Test caching patterns for PPT Generator"""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    print("\n🔄 Testing PPT Generator caching patterns...")
    
    # Cache user session
    user_session = {
        'user_id': 'user_123',
        'username': 'testuser',
        'permissions': ['create_presentation', 'edit_presentation'],
        'last_active': datetime.now().isoformat()
    }
    
    # Cache with 1 hour expiration
    r.setex('session:user_123', 3600, json.dumps(user_session))
    print("✅ User session cached")
    
    # Cache presentation metadata
    presentation_meta = {
        'id': 'pres_789',
        'title': 'My Test Presentation',
        'slide_count': 10,
        'theme': 'professional',
        'last_modified': datetime.now().isoformat()
    }
    
    r.hset('presentations:pres_789:meta', mapping=presentation_meta)
    print("✅ Presentation metadata cached")
    
    # Cache processed document content
    document_content = {
        'document_id': 'doc_456',
        'extracted_text': 'This is extracted content from PDF...',
        'page_count': 5,
        'processing_time': 2.5
    }
    
    # Cache for 30 minutes
    r.setex('documents:doc_456:content', 1800, json.dumps(document_content))
    print("✅ Document content cached")
    
    # Test retrieval
    cached_session = json.loads(r.get('session:user_123'))
    cached_meta = r.hgetall('presentations:pres_789:meta')
    cached_content = json.loads(r.get('documents:doc_456:content'))
    
    print(f"✅ Retrieved session: {cached_session['username']}")
    print(f"✅ Retrieved presentation: {cached_meta['title']}")
    print(f"✅ Retrieved document: {len(cached_content['extracted_text'])} characters")

if __name__ == "__main__":
    print("🧪 Testing Redis setup for PPT Generator...")
    
    if test_redis_connection():
        test_caching_patterns()
        print("\n🎯 Redis is ready for PPT Generator microservices!")
    else:
        print("\n❌ Please check Redis setup")