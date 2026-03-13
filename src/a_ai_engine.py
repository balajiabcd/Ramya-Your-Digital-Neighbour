import chromadb
import os
from openai import OpenAI
from datetime import datetime
from src.c_rag_engine import get_memories
import time
import logging
import yaml
import json

logger = logging.getLogger(__name__)



class RamyaBot:




    # Initialize the bot
    def __init__(self, api_key, user_email=None):
        self.user_email = user_email
        self.user_prefix = self._get_user_prefix(user_email)
        
        # Load Model Rankings from .env or fallback to defaults
        self.MODEL_RANKING = self._load_model_ranking()
        logger.info(f"Loaded {len(self.MODEL_RANKING)} models from configuration")

        # Initialize Vector DB on your A: drive
        self.Ramya_role =   """
                            You are Ramya, a helpful friend. Reply only in English. 
                            You give one paragraph reply unless needed.
                            You dont write useless word or words.
                            """
        try:
            db_path = os.getenv("CHROMADB_PATH", 'ramya_memory_db')
            self.chroma_client = chromadb.PersistentClient(path=db_path)
            # System-wide settings and user profiles
            self.settings_col = self.chroma_client.get_or_create_collection(name="bot_settings")
            self.profiles_col = self.chroma_client.get_or_create_collection(name="user_profiles")
            
            if self.user_email:
                self._update_user_stats()
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise RuntimeError("Database connection failed. Please check if another process is using it.")

        self.client = OpenAI(   base_url="https://openrouter.ai/api/v1",
                                api_key=api_key )
        self.current_collection = None
        
        
        # Try to load existing index
        saved_data = self.settings_col.get(ids=["model_state"])
        if saved_data['metadatas']:
            meta = saved_data['metadatas'][0]
            self.current_model_index = meta.get("index", 1)
            self.last_reset_date = datetime.strptime(meta.get("date"), '%Y-%m-%d').date()
        else:
            self.last_reset_date = datetime.now().date()
            self.current_model_index = 1


        today = datetime.now().date()
        if today > self.last_reset_date:
            print(f"DEBUG: New day detected ({today}). Resetting model index to 1.")
            self.current_model_index = 1
            self.last_reset_date = today
            self.settings_col.upsert(   ids=["model_state"],
                                        metadatas=[{"index": self.current_model_index, "date": str(self.last_reset_date)}],
                                        documents=["System state tracking"] )


        self.chat_session = None
        self.summary = ""
        self.history = [{"role": "system", "content": self.Ramya_role}]

    def _load_model_ranking(self):
        """Load model ranking from .env file or return default fallback."""
        fallback_models = {
            1: "nousresearch/hermes-3-llama-3.1-405b:free",
            2: "google/gemini-2.0-flash-exp:free",
            3: "deepseek/deepseek-r1:free",
            4: "qwen/qwen-2.5-72b-instruct:free",
            5: "meta-llama/llama-3.2-1b-instruct:free",
            6: "huggingfaceh4/zephyr-7b-beta:free",
            7: "mistralai/mistral-7b-instruct:free",
            8: "openchat/openchat-7b:free",
            9: "undi95/toppy-m-7b:free",
            10: "gryphe/mythomist-7b:free",
            11: "nousresearch/nous-capybara-7b:free",
            12: "pygmalionai/mythalion-13b:free",
            13: "z-ai/glm-4.5-air:free",
            14: "nvidia/nemotron-3-super:free",
            15: "nvidia/nemotron-3-nano-30b-a3b:free",
            16: "arcee-ai/trinity-mini:free",
            17: "nvidia/nemotron-nano-9b-v2:free",
            18: "nvidia/nemotron-nano-12b-2-vl:free",
            19: "openai/gpt-oss-120b:free",
            20: "qwen/qwen3-coder-480b-a35b-instruct:free",
            21: "qwen/qwen3-next-80b-a3b-instruct:free",
            22: "liquidai/lfm-2.5-1.2b-thinking:free",
            23: "liquidai/lfm-2.5-1.2b-instruct:free",
            24: "openai/gpt-oss-20b:free",
            25: "mistralai/mistral-small-3.1-24b-instruct:free",
            26: "qwen/qwen3-4b-instruct:free",
            27: "venice/uncensored:free",
            28: "nousresearch/hermes-3-405b-instruct:free",
            29: "google/gemma-3-4b-it:free",
            30: "google/gemma-3n-4b-it:free",
            31: "google/gemma-3n-2b-it:free",
            32: "google/gemma-3-12b-it:free",
            33: "nvidia/llama-nemotron-embed-vl-1b-v2:free"
        }
        
        try:
            # Try loading from .env file first
            model_ranking_json = os.getenv("MODEL_RANKING")
            if model_ranking_json:
                model_dict = json.loads(model_ranking_json)
                # Convert string keys to integers
                model_ranking = {int(k): v for k, v in model_dict.items()}
                logger.info("Model ranking loaded from .env (MODEL_RANKING)")
                return model_ranking
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse MODEL_RANKING from .env: {e}. Checking config.yaml...")
        
        # Try loading from config.yaml if exists
        config_path = os.getenv("CONFIG_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml'))
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and 'models' in config and 'ranking' in config['models']:
                        model_ranking = {int(k): v for k, v in config['models']['ranking'].items()}
                        logger.info("Model ranking loaded from config.yaml")
                        return model_ranking
            except Exception as e:
                logger.warning(f"Failed to load config.yaml: {e}")
        
        # Return fallback defaults
        logger.info("Using default fallback model ranking (15 models)")
        return fallback_models

    def _get_user_prefix(self, email):
        """Creates a safe prefix from the user's email."""
        if not email:
            return "anon"
        # Sanitize email: remove special chars, keep alphanumeric and underscores
        safe_email = "".join(c for c in email if c.isalnum() or c == '_').lower()
        return safe_email[:30] # Keep it reasonably short

    def _get_coll_name(self, chat_name):
        """Internal helper to get the full collection name including user isolation."""
        # Sanitize chat_name for ChromaDB (3-63 chars, alphanumeric, underscores, hyphens, dots)
        safe_chat = "".join(c for c in chat_name if c.isalnum() or c in "_-.")
        if len(safe_chat) < 3:
            safe_chat = f"chat_{safe_chat}" if safe_chat else "new_chat"
        
        full_name = f"{self.user_prefix}_{safe_chat}"
        return full_name[:63]

    def _update_user_stats(self):
        """Updates last login and maintains message count in user profiles."""
        try:
            now = datetime.now().isoformat()
            existing = self.profiles_col.get(ids=[self.user_prefix])
            
            total_messages = 0
            if existing and existing['metadatas']:
                total_messages = existing['metadatas'][0].get('total_messages', 0)
            
            self.profiles_col.upsert(
                ids=[self.user_prefix],
                metadatas=[{
                    "email": self.user_email,
                    "last_login": now,
                    "total_messages": total_messages
                }],
                documents=[f"Profile for {self.user_email}"]
            )
            logger.info(f"Updated stats for user: {self.user_prefix}")
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")

    def increment_message_count(self):
        """Increments total_messages for the current user."""
        try:
            existing = self.profiles_col.get(ids=[self.user_prefix])
            if existing and existing['metadatas']:
                meta = existing['metadatas'][0]
                meta['total_messages'] = meta.get('total_messages', 0) + 1
                self.profiles_col.update(ids=[self.user_prefix], metadatas=[meta])
        except Exception as e:
            logger.error(f"Error incrementing message count: {e}")



    # called by app.py, Starting a new chat
    def start_new_chat(self, chat_name):
        full_name = self._get_coll_name(chat_name)
        
        # Load the specific memory from ChromaDB
        self.current_collection = self.chroma_client.get_or_create_collection(name=full_name)
        self.history = [{"role": "system", "content": self.Ramya_role}]
        
        # Load recent history into context
        try:
            results = self.current_collection.get()
            docs = results['documents']
            ids = results['ids']
            if ids:
                def sort_key(id_str):
                    try:
                        parts = id_str.split('_')
                        if parts[0] == 'id' and len(parts) > 1: return (0, int(parts[1]))
                        if parts[0] == 'msg' and len(parts) > 1: return (1, int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
                        return (2, id_str)
                    except: return (3, id_str)
                paired = sorted(zip(ids, docs), key=lambda x: sort_key(x[0]))
                
                # Take last 10 messages for short-term memory
                for p in paired[-10:]:
                    text = p[1]
                    if text.startswith("User said: "):
                        self.history.append({"role": "user", "content": text.replace("User said: ", "", 1)})
                    elif text.startswith("Ramya replied: "):
                        self.history.append({"role": "assistant", "content": text.replace("Ramya replied: ", "", 1)})
        except Exception as e:
            print(f"Error loading context history: {e}")
            
        return full_name


    # called by app.py, Getting all chats
    def get_all_chats(self):
        """Returns a list of all chat names belonging to the current user."""
        try:
            collections = self.chroma_client.list_collections()
            all_names = [getattr(c, 'name', str(c)) for c in collections]
            
            user_chats = []
            prefix = f"{self.user_prefix}_"
            for name in all_names:
                if name.startswith(prefix):
                    # Strip the user prefix to show original chat name to the user
                    user_chats.append(name[len(prefix):])
            return user_chats
        except Exception:
            return []



    # called by app.py, Deleting a chat
    def delete_chat(self, chat_name):
        """Deletes a user-specific chat collection."""
        try:
            full_name = self._get_coll_name(chat_name)
            self.chroma_client.delete_collection(name=full_name)
            if self.current_collection and self.current_collection.name == chat_name:
                self.current_collection = None
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False



    # called by app.py, Getting chat history
    def get_chat_history(self, chat_name):
        """Retrieves and sorts the history of a specific chat for the current user."""
        try:
            full_name = self._get_coll_name(chat_name)
            collection = self.chroma_client.get_collection(name=full_name)
            results = collection.get()
            # Sort documents by ID (id_1, id_2...) to preserve chronological order
            # Pairing IDs with documents for easy sorting
            docs = results['documents']
            ids = results['ids']
            metadatas = results.get('metadatas', [])
            
            if not ids: return []
            
            # Use a robust sort key to handle both old 'id_N' and new 'msg_timestamp_seq' formats
            def sort_key(id_str):
                try:
                    parts = id_str.split('_')
                    if parts[0] == 'id' and len(parts) > 1:
                        return (0, int(parts[1])) # Old format
                    if parts[0] == 'msg' and len(parts) > 1:
                        return (1, int(parts[1]), int(parts[2]) if len(parts) > 2 else 0) # New format
                    return (2, id_str)
                except:
                    return (3, id_str)
            
            # Helper to extract timestamp from ID or metadata
            def extract_timestamp(id_str, meta):
                # Try metadata first
                if meta and meta.get('timestamp'):
                    return meta.get('timestamp')
                # Try to extract from ID (format: msg_{ts}_1 or id_{ts})
                try:
                    parts = id_str.split('_')
                    if parts[0] == 'msg' and len(parts) > 1:
                        return int(parts[1])
                    if parts[0] == 'id' and len(parts) > 1:
                        return int(parts[1]) * 1000  # Convert to milliseconds
                except:
                    pass
                return None
            
            paired = sorted(zip(ids, docs, metadatas), key=lambda x: sort_key(x[0]))
            # Return list of dicts with message text and timestamp
            return [
                {
                    'text': p[1], 
                    'timestamp': extract_timestamp(p[0], p[2])
                } 
                for p in paired
            ]
        except Exception as e:
            print(f"History retrieval error for {chat_name}: {e}")
            return []



    # called by app.py, Getting response as a generator for streaming
    def get_response(self, user_input):
        if not self.current_collection:
            chat_name = user_input.strip()[:30]
            self.start_new_chat(chat_name)

        # RAG Step: Get relevant memories
        relevant_memories = get_memories(self.current_collection, user_input, client=self.client)
        
        current_messages = self.history + [ 
            {"role": "user", "content": f"Context from past: {relevant_memories}\nUser: {user_input}"}  ]

        # BACKGROUND STRING ACCUMULATOR
        full_response_accumulator = [] 
        active_api_stream = None
        
        # yield " . " # Remove leading space
        
        try:
            active_api_stream = self._call_with_fallback(current_messages, max_tokens=1000, stream=True)
            
            if active_api_stream is None:
                error_msg = "Sorry, all AI models failed to respond or are unavailable."
                yield error_msg
                full_response_accumulator.append(error_msg)
            elif isinstance(active_api_stream, str): 
                yield active_api_stream
                full_response_accumulator.append(active_api_stream)
            else:
                for chunk in active_api_stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        full_response_accumulator.append(token)
                        yield token
                
                print("DEBUG: Stream 'Done' signal received.")

        except GeneratorExit:
            # THIS IS THE SIGNAL HANDLER FOR USER DISCONNECT (Navigating away/closing window)
            print("DEBUG: User disconnected mid-stream. Closing active API stream and aborting save.")
            if active_api_stream and hasattr(active_api_stream, 'close'):
                active_api_stream.close()
            # DISCARD the accumulated buffer explicitly
            full_response_accumulator.clear()
            # We return immediately to skip the background finalization
            return 

        except Exception as e:
            error_msg = f"Sorry, I'm having trouble processing that right now. ({e})"
            yield error_msg
            full_response_accumulator.append(error_msg)

        # Finalize the accumulated string (Only runs if stream finished normally)
        ramya_text_full = "".join(full_response_accumulator)

        # Trigger the "Background" task ONLY if reached (not aborted by GeneratorExit)
        import threading
        bg_thread = threading.Thread(target=self._finalize_interaction, args=(user_input, ramya_text_full))
        bg_thread.start()

        return 




    # Post-processing: Facts extraction and Saving (Asynchronous/Background)
    def _finalize_interaction(self, user_msg, bot_msg):
        try:
            # 1. Extract Summary Facts (Sync within thread)
            combined_summary = ""
            extraction_messages = [ 
                {"role": "system", "content": "You are a data extractor. Extract 2 key facts as short bullet points starting with 'FACT:'."},
                {"role": "user", "content": bot_msg} 
            ]
            fact_text = self._call_with_fallback(extraction_messages, max_tokens=500, stream=False)
            if fact_text:
                summary_list = [f.replace("FACT:", "").strip() for f in fact_text.split('\n') if "FACT:" in f]
                combined_summary = "\n".join(summary_list)

            # 2. Add to ChromaDB Memory
            self.save_interaction(user_msg, bot_msg, combined_summary)
            self.increment_message_count() # Track engagement
            self.summary = combined_summary
            self.history.append({"role": "user", "content": user_msg})
            self.history.append({"role": "assistant", "content": bot_msg})
            
            print(f"DEBUG: Background finalization complete.")
        except Exception as ex:
            print(f"ERROR in background finalization: {ex}")

    # called by get_response function in this file (above one)
    def save_interaction(self, user_input, message_text, combined_summary):
        try:
            # Generate unique timestamp-based IDs
            ts = int(time.time() * 1000)
            user_id = f"msg_{ts}_1"
            bot_id = f"msg_{ts}_2"
            
            self.current_collection.add(
                documents=[f"User said: {user_input}", f"Ramya replied: {message_text}"],
                ids=[user_id, bot_id],
                metadatas=[ {"type":"user","summary": "", "timestamp": ts},
                            {"type":"ramya","summary": combined_summary, "timestamp": ts}]   )
        except Exception as e:
            print(f"ChromaDB Add Error: {e}")



    # called by get_response function in this file (above one), Calling the LLM with automatic model fallback and daily reset
    def _call_with_fallback(self, messages, max_tokens=500, stream=False):
        max_idx = max(self.MODEL_RANKING.keys())
        text = None
        text_none_count = 0
        while self.current_model_index <= max_idx and text_none_count < 2:
            model = self.MODEL_RANKING.get(self.current_model_index)
            try:
                print(f"DEBUG: Attempting with model: {model} (Index: {self.current_model_index})")
                print("____________________________________________________________________________")
                response = self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            max_tokens=max_tokens,
                            stream=stream                )
                
                if stream:
                    return response

                try:                
                    text = response.choices[0].message.content
                    if text in ("", None):
                        print("text is empty or None")
                        text_none_count += 1
                        continue
                except Exception as e:
                    text = f"Error while extracting data from responce: {model}: {e}"
                break
            
            
            except Exception as e:
                print("Changing model index")
                print(f"Error with model {model}: {e}")
                self.current_model_index += 1
                if self.current_model_index > max_idx:
                    text = None
                    break


        self.settings_col.upsert(   ids=["model_state"],
                                    metadatas=[{"index": self.current_model_index, "date": str(self.last_reset_date)}],
                                    documents=["System state tracking"] )
        return text



    def check_health(self):
        """
        Checks the health of the bot's dependencies (ChromaDB and OpenRouter/OpenAI).
        """
        health_status = {
            "database": {"status": "offline", "details": None},
            "ai_engine": {"status": "offline", "details": None}
        }

        # Check ChromaDB
        try:
            # heartbeat() returns a high-res timestamp if alive
            if self.chroma_client.heartbeat():
                health_status["database"]["status"] = "online"
        except Exception as e:
            health_status["database"]["details"] = str(e)

        # Check AI Engine (OpenRouter)
        try:
            # We'll do a minimal model list call to verify connectivity and API key
            self.client.models.list()
            health_status["ai_engine"]["status"] = "online"
        except Exception as e:
            health_status["ai_engine"]["details"] = str(e)

        return health_status
