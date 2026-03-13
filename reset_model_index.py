#!/usr/bin/env python3
"""
Reset the model index to 1 in ChromaDB
"""
import chromadb
from datetime import datetime

# Connect to ChromaDB
db_path = 'ramya_memory_db'
chroma_client = chromadb.PersistentClient(path=db_path)

# Get the bot_settings collection
settings_col = chroma_client.get_or_create_collection(name="bot_settings")

# Reset the model index to 1
today = datetime.now().date()
settings_col.upsert(
    ids=["model_state"],
    metadatas=[{"index": 1, "date": str(today)}],
    documents=["System state tracking"]
)

print(f"✅ Model index reset to 1 for {today}")
print("Now restart the app to start from Model 1")
