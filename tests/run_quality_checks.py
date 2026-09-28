import os
import sys
import pandas as pd
import snowflake.connector
from data_quality_check import validate_stock_prices, validate_company_profiles

def main():
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"], 
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"], 
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "lakehouse_wh"),
        database="LAKEHOUSE_DB", 
        schema="GOLD"
    )

    def load(table):
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        # .lower() matches Snowflake's uppercase output to your validator's lowercase expectations
        df = pd.DataFrame(cur.fetchall(), columns=[c[0].lower() for c in cur.description])
        return df

    print("Fetching staging tables for quality validation...")
    
    # Using all() or an explicit 'and' ensures both tables are evaluated
    ok = (
        validate_stock_prices(load("stg_stock_prices")) and 
        validate_company_profiles(load("stg_company_profiles"))
    )
    
    if not ok:
        print("CRITICAL: Data Quality Gates Failed. Halting pipeline.")
        sys.exit(1)
        
    print("SUCCESS: Data Quality Gates Passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()