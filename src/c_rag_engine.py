import chromadb

def get_memories(collection, user_input, client=None):
    """
    Search Vector DB for past conversations and return:
    1. Recent memories: 2 most recent conversations
    2. Related memories: 2 most semantically similar conversations
    
    Each memory pair contains user message and Ramya's summary.
    Format: "user: <message>\\nRamya: <summary>"
    """
    n_results = 6
    
    if not collection:
        return ""
    
    try:
        results = collection.query(
            query_texts=[user_input],
            n_results=n_results,
            where={"type": "ramya"},
            include=["metadatas", "ids", "documents"]
        )
        
        if not results['ids'] or not results['ids'][0]:
            return ""
        
        paired_data = []
        for i in range(len(results['ids'][0])):
            bot_id = results['ids'][0][i]
            bot_meta = results['metadatas'][0][i]
            
            if not bot_meta or 'summary' not in bot_meta or not bot_meta['summary']:
                continue
            
            ts = bot_meta.get('timestamp', 0)
            topic = bot_meta.get('topic_name', '')
            summary = bot_meta['summary']
            
            user_id = f"msg_{ts}_1"
            
            try:
                user_result = collection.get(ids=[user_id], include=["documents"])
                user_doc = ""
                if user_result['documents'] and user_result['documents'][0]:
                    user_doc = user_result['documents'][0].replace("User said: ", "")
            except:
                user_doc = ""
            
            paired_data.append({
                'user': user_doc,
                'ramya': summary,
                'timestamp': ts,
                'id': bot_id
            })
        
        if not paired_data:
            return ""
        
        paired_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        recent = paired_data[:2]
        
        related = sorted(paired_data[2:], key=lambda x: x['id'], reverse=True)[:2]
        
        def format_memory(item):
            return f"user: {item['user']}\nRamya: {item['ramya']}"
        
        output_parts = []
        
        if recent:
            output_parts.append("Recent:")
            for item in recent:
                output_parts.append(format_memory(item))
        
        if related:
            if output_parts:
                output_parts.append("")
            output_parts.append("Related:")
            for item in related:
                output_parts.append(format_memory(item))
        
        return "\n".join(output_parts) if output_parts else ""

    except Exception as e:
        print(f"ChromaDB Query Error: {e}")
        return ""
