import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
import os
import json

PROJECT_ROOT = r"C:\Users\deepa\OneDrive\Desktop\engagement-risk-platform"

class PlayerVectorDB:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=os.path.join(PROJECT_ROOT, "app", "database", "chroma_db"))
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection_name = "player_profiles"
        self._init_collection()
    
    def _init_collection(self):
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn
            )
    
    def index_players(self, users_df):
        """Index all players into the vector database."""
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )
        
        documents = []
        metadatas = []
        ids = []
        
        for _, row in users_df.iterrows():
            doc = f"""
            Player {row['user_id']}: 
            Age {row['age']}, from {row['state']}. 
            Segment: {row['segment']}. 
            Total spend: ${row['total_spend']}. 
            Visits every {row['visit_frequency']} days. 
            Risk score: {row['risk_score']} ({row['risk_level']} risk).
            Plays: {row['game_types']}.
            """
            
            documents.append(doc)
            metadatas.append({
                'user_id': int(row['user_id']),
                'age': int(row['age']),
                'state': row['state'],
                'segment': row['segment'],
                'total_spend': float(row['total_spend']),
                'visit_frequency': int(row['visit_frequency']),
                'risk_score': float(row['risk_score']),
                'risk_level': row['risk_level']
            })
            ids.append(f"player_{row['user_id']}")
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Indexed {len(ids)} players in vector database.")
    
    def search(self, query, n_results=10):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def search_with_filters(self, query, n_results=10, filters=None):
        """
        Search with metadata filters.
        filters: dict with keys like 'risk_level', 'segment', 'state'
        """
        if filters:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filters
            )
        else:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
        return results

if __name__ == "__main__":
    db = PlayerVectorDB()
    
    users_df = pd.read_csv(os.path.join(PROJECT_ROOT, "app", "data", "users.csv"))
    
    db.index_players(users_df)
    
    print("\nTesting search...")
    results = db.search("high-risk players in California", n_results=5)
    for i, meta in enumerate(results['metadatas'][0]):
        print(f"{i+1}. Player {meta['user_id']} - {meta['state']} - Risk: {meta['risk_level']}")
    
    print("\nTesting search with risk filter...")
    results = db.search_with_filters("players in California", n_results=5, filters={"risk_level": "High"})
    for i, meta in enumerate(results['metadatas'][0]):
        print(f"{i+1}. Player {meta['user_id']} - {meta['state']} - Risk: {meta['risk_level']}")