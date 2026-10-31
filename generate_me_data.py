import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


np.random.seed(42)

def generate_ngo_data():
    print("Generating 6-month M&E financial and epidemiological dataset...")

    counties = ['Turkana', 'Kilifi', 'Kisumu', 'Garissa', 'Kitui']
    programs = ['Malaria Prevention & Nets', 'Maternal & Child Health Clinic']
    
    coordinates = {
        'Turkana': (3.1166, 35.5973),
        'Kilifi': (-3.5107, 39.9093),
        'Kisumu': (-0.0917, 34.7680),
        'Garissa': (0.4532, 39.6460),
        'Kitui': (-1.3667, 38.0167)
    }

    data = []
    record_id = 1

    start_date = datetime.now() - timedelta(weeks=24)

    for week in range(1, 25):
        report_date = start_date + timedelta(weeks=week)
        
        for county in counties:
            for program in programs:
                allocated_budget = np.random.randint(500000, 2000000) # KES
                burn_rate = np.random.uniform(0.65, 0.95)
                spent_budget = int(allocated_budget * burn_rate)
                
                if program == 'Malaria Prevention & Nets':
                    target_beneficiaries = 2000
                    reached_beneficiaries = int(target_beneficiaries * np.random.uniform(0.7, 1.1))
                    
                    health_impact_pct = round(np.random.uniform(15.0, 40.0), 1) if reached_beneficiaries >= 1500 else round(np.random.uniform(2.0, 10.0), 1)
                else:
                    target_beneficiaries = 800
                    reached_beneficiaries = int(target_beneficiaries * np.random.uniform(0.6, 1.05))
                    
                    health_impact_pct = round(np.random.uniform(20.0, 45.0), 1) if reached_beneficiaries >= 600 else round(np.random.uniform(5.0, 15.0), 1)

                cost_per_beneficiary = round(spent_budget / reached_beneficiaries, 2) if reached_beneficiaries > 0 else 0
                
                if burn_rate > 0.85 and (reached_beneficiaries / target_beneficiaries) >= 0.8:
                    status = "On Track 🟢"
                elif burn_rate > 0.90 and (reached_beneficiaries / target_beneficiaries) < 0.7:
                    status = "At Risk (High Spend, Low Reach) 🔴"
                else:
                    status = "Moderate / Monitoring 🟡"

                lat, lon = coordinates[county]

                data.append({
                    'report_id': f"ME-{2000 + record_id}",
                    'week_number': week,
                    'report_date': report_date.strftime('%Y-%m-%d'),
                    'county': county,
                    'program_name': program,
                    'allocated_budget': allocated_budget,
                    'spent_budget': spent_budget,
                    'target_beneficiaries': target_beneficiaries,
                    'reached_beneficiaries': reached_beneficiaries,
                    'cost_per_beneficiary': cost_per_beneficiary,
                    'health_impact_reduction_pct': health_impact_pct,
                    'project_status': status,
                    'latitude': lat,
                    'longitude': lon
                })
                record_id += 1

    df = pd.DataFrame(data)
    return df

def save_to_sqlite(df, db_path='data/project_data.db'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    df.to_sql('me_reports', conn, if_exists='replace', index=False)
    conn.close()
    print(f"Successfully saved M&E database to {db_path} with {len(df)} records.")

if __name__ == '__main__':
    df = generate_ngo_data()
    save_to_sqlite(df)