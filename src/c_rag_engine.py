import chromadb

def get_memories(collection, user_input, client=None):
    n_results = 2  # Fetch more to allow for recency filtering
    """Search Vector DB for similar past messages and prioritize the most recent ones."""
    if not collection:
        return ""
        
    try:
        results = collection.query(
            query_texts=[user_input],
            n_results=n_results,
            where={"type": "ramya"},
            include=["metadatas", "ids"]
        )
        
        memories = []
        if results['metadatas'] and results['ids']:
            # Pair IDs with metadata for sorting
            paired = []
            for i in range(len(results['ids'][0])):
                id_val = results['ids'][0][i]
                meta = results['metadatas'][0][i]
                if meta and 'summary' in meta and meta['summary']:
                    paired.append((id_val, meta['summary']))
            
            # Sort by ID descending (relying on msg_TIMESTAMP_SEQ format where higher = newer)
            paired.sort(key=lambda x: x[0], reverse=True)
            
            # Take the top 2 newest from the semantically relevant batch
            memories = [p[1] for p in paired[:2]]
        
        return "\n".join(memories) if memories else "No relevant past memories found."

    except Exception as e:
        print(f"ChromaDB Query Error: {e}")
        return ""

