import pandas as pd
import numpy as np
import requests
import random
from faker import Faker
from datetime import datetime, timedelta
import os
import json

fake = Faker(['en_US'])
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# ============================================
# FETCH REAL DATA FROM CENSUS API
# ============================================
CENSUS_API_KEY = "ce25628a0082783dbbef012acbf85a783e2eebf9"

def fetch_census_demographics():
    """Fetch real US demographic data by state from Census API."""
    try:
        url = f"https://api.census.gov/data/2021/acs/acs1?get=NAME,B01001_001E,B01001_002E,B01001_026E,B19013_001E&for=state:*&key={CENSUS_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️ Census API returned {response.status_code}. Using fallback data.")
            return get_fallback_demographics()
        
        data = response.json()
        headers = data[0]
        state_data = data[1:]
        
        demographics = {}
        for row in state_data:
            state_name = row[0]
            total_pop = int(row[1]) if row[1] else 0
            male_pop = int(row[2]) if row[2] else 0
            female_pop = int(row[3]) if row[3] else 0
            median_income = int(row[4]) if row[4] else 0
            
            demographics[state_name] = {
                'total_pop': total_pop,
                'male_pop': male_pop,
                'female_pop': female_pop,
                'median_income': median_income
            }
        
        print(f"✅ Fetched real Census data for {len(demographics)} states.")
        return demographics
    
    except Exception as e:
        print(f"❌ Error fetching Census data: {e}")
        return get_fallback_demographics()

def get_fallback_demographics():
    """Return fallback demographic data if Census API fails."""
    print("Using fallback demographic data.")
    return {
        'California': {'total_pop': 39538223, 'male_pop': 19643234, 'female_pop': 19894989, 'median_income': 84597},
        'Texas': {'total_pop': 29145505, 'male_pop': 14498510, 'female_pop': 14646995, 'median_income': 67598},
        'Florida': {'total_pop': 21538187, 'male_pop': 10568571, 'female_pop': 10969616, 'median_income': 63721},
        'New York': {'total_pop': 20201249, 'male_pop': 9805933, 'female_pop': 10395316, 'median_income': 74307},
        'Pennsylvania': {'total_pop': 13002700, 'male_pop': 6377803, 'female_pop': 6624897, 'median_income': 67204},
        'Illinois': {'total_pop': 12812508, 'male_pop': 6293703, 'female_pop': 6518805, 'median_income': 72563},
        'Ohio': {'total_pop': 11799448, 'male_pop': 5800458, 'female_pop': 5998990, 'median_income': 61743},
        'Georgia': {'total_pop': 10711908, 'male_pop': 5256057, 'female_pop': 5455851, 'median_income': 65927},
        'North Carolina': {'total_pop': 10439388, 'male_pop': 5103675, 'female_pop': 5340713, 'median_income': 61234},
        'Michigan': {'total_pop': 10077331, 'male_pop': 4973202, 'female_pop': 5104129, 'median_income': 62827}
    }

def generate_risk_score(age, total_spend, visit_frequency, median_income):
    """Generate risk score based on real demographic factors."""
    base_risk = 0
    
    if age < 25 or age > 60:
        base_risk += 15
    
    if total_spend > 2000:
        base_risk += 30
    elif total_spend > 1000:
        base_risk += 15
    
    if visit_frequency < 5:
        base_risk += 20
    elif visit_frequency < 10:
        base_risk += 10
    
    if median_income < 50000:
        base_risk += 10
    elif median_income > 100000:
        base_risk -= 5
    
    risk_score = max(0, min(100, base_risk + random.randint(-10, 20)))
    return risk_score

def generate_users_with_census(census_data, n=1000):
    """Generate users with real demographic context from Census data."""
    segments = ['Casual', 'Regular', 'Frequent', 'High-Value', 'VIP']
    game_types_list = ['Slots', 'Table Games', 'Sports', 'Poker', 'Bingo']
    
    state_list = list(census_data.keys())
    
    users = []
    for i in range(1, n + 1):
        state = random.choice(state_list)
        demo = census_data[state]
        
        age = random.randint(19, 75)
        total_spend = round(random.uniform(10, 5000), 2)
        visit_frequency = random.randint(1, 30)
        
        risk_score = generate_risk_score(age, total_spend, visit_frequency, demo['median_income'])
        
        risk_level = 'Low' if risk_score < 30 else 'Medium' if risk_score < 60 else 'High'
        
        users.append({
            'user_id': i,
            'age': age,
            'state': state,
            'median_income': demo['median_income'],
            'segment': random.choice(segments),
            'join_date': fake.date_between(start_date='-3y', end_date='-1d'),
            'total_spend': total_spend,
            'visit_frequency': visit_frequency,
            'avg_session_time': round(random.uniform(5, 120), 1),
            'game_types': ', '.join(random.sample(game_types_list, k=random.randint(1, 3))),
            'risk_score': risk_score,
            'risk_level': risk_level
        })
    
    return pd.DataFrame(users)

def generate_transactions(users, n=3000):
    """Generate synthetic transaction history."""
    transaction_types = ['Deposit', 'Withdrawal', 'Bet']
    game_types = ['Slots', 'Table Games', 'Sports', 'Poker', 'Bingo']
    
    transactions = []
    for _ in range(n):
        user = users.sample(1).iloc[0]
        transactions.append({
            'transaction_id': len(transactions) + 1,
            'user_id': user['user_id'],
            'amount': round(random.uniform(5, 500), 2),
            'transaction_type': random.choice(transaction_types),
            'game_type': random.choice(game_types),
            'timestamp': fake.date_time_between(start_date='-3y', end_date='now')
        })
    return pd.DataFrame(transactions)

def save_data():
    """Generate and save all data with Census integration."""
    print("🚀 Fetching real demographic data from US Census API...")
    census_data = fetch_census_demographics()
    
    print("Generating users with real demographic context...")
    users = generate_users_with_census(census_data, 1000)
    print(f"✅ Generated {len(users)} users with real US demographic data.")
    
    print("Generating transactions...")
    transactions = generate_transactions(users, 3000)
    print(f"✅ Generated {len(transactions)} transactions.")
    
    users.to_csv('app/data/users.csv', index=False)
    transactions.to_csv('app/data/transactions.csv', index=False)
    
    print("✅ Data saved to app/data/users.csv and app/data/transactions.csv")
    
    print("\n📊 Risk Level Distribution:")
    print(users['risk_level'].value_counts())
    
    print("\n📊 Top States by User Count:")
    print(users['state'].value_counts().head(10))

if __name__ == "__main__":
    save_data()