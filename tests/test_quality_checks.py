import great_expectations as gx
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def evaluate_validation_results(validator, dataset_name: str) -> bool:
    validation_result = validator.validate()
    
    if not validation_result.success:
        logging.error(f"Data Quality Checks FAILED for {dataset_name}.")
        
        for result in validation_result.results:
            if not result.success:
                config = result.expectation_config
                res_details = result.result
                
                logging.error(f"--- Failed Expectation: {config.expectation_type} ---")
                logging.error(f"Target/Params: {config.kwargs}")
                
                # Safely extract specific failure details if they exist in the result dictionary
                if isinstance(res_details, dict):
                    if 'unexpected_count' in res_details:
                        logging.error(f"Unexpected Count: {res_details.get('unexpected_count')}")
                    if 'unexpected_list' in res_details:
                        logging.error(f"Unexpected Values: {res_details.get('unexpected_list')}")
        return False
        
    logging.info(f"Data Quality Checks PASSED for {dataset_name}.")
    return True

def validate_company_profiles(df: pd.DataFrame) -> bool:
    """Defines data quality checks for the Company Profiles DataFrame."""
    logging.info("Starting Great Expectations validation for Company Profiles...")
    
    context = gx.get_context(mode="ephemeral")
    validator = context.sources.pandas_default.read_dataframe(df)
    
    # Define rules
    validator.expect_column_values_to_not_be_null(column="symbol")
    validator.expect_column_values_to_not_be_null(column="company_name")
    validator.expect_column_values_to_be_unique(column="symbol")
    validator.expect_table_row_count_to_be_between(min_value=1, max_value=500)
    
    return evaluate_validation_results(validator, "Company Profiles")

def validate_stock_prices(df: pd.DataFrame) -> bool:
    """Defines data quality checks for the Stock Prices DataFrame."""
    logging.info("Starting Great Expectations validation for Stock Prices...")
    
    context = gx.get_context(mode="ephemeral")
    validator = context.sources.pandas_default.read_dataframe(df)
    
    # Define rules
    validator.expect_column_values_to_not_be_null(column="symbol")
    validator.expect_column_values_to_not_be_null(column="price_date")
    validator.expect_column_values_to_not_be_null(column="close")
    
    validator.expect_column_values_to_be_between(column="close", min_value=0.01)
    validator.expect_column_values_to_be_between(column="volume", min_value=0)
    
    if "high" in df.columns and "low" in df.columns:
        # FIX: Capitalized the A and B in the method name
        validator.expect_column_pair_values_A_to_be_greater_than_B(
            column_A="high", 
            column_B="low", 
            or_equal=True
        )
    
    validator.expect_table_row_count_to_be_between(min_value=1)
    
    return evaluate_validation_results(validator, "Stock Prices")

# --- Local Testing Block ---
if __name__ == "__main__":
    print("Testing a VALID dataframe...")
    valid_prices = pd.DataFrame({
        "symbol": ["AAPL", "MSFT"],
        "price_date": ["2026-09-27", "2026-09-27"],
        "open": [150.00, 310.00],
        "high": [152.00, 315.00],
        "low": [149.00, 308.00],
        "close": [150.50, 310.20],
        "volume": [1000, 2000]
    })
    validate_stock_prices(valid_prices)
    
    print("\nTesting an INVALID dataframe (negative price & high < low)...")
    invalid_prices = pd.DataFrame({
        "symbol": ["AAPL"],
        "price_date": ["2026-09-27"],
        "open": [150.00],
        "high": [145.00],   
        "low": [149.00],    
        "close": [-50.00],  
        "volume": [1000]
    })
    validate_stock_prices(invalid_prices)