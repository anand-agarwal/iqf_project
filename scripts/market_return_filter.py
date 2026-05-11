import pandas as pd
from datetime import datetime
import glob
import os

# Generate month-end dates from Dec 2020 to Jan 2026
def generate_month_end_dates(start_date, end_date):
    dates = pd.date_range(start=start_date, end=end_date, freq='ME')
    return dates

# Month-end dates
month_ends = generate_month_end_dates('2020-12-31', '2026-01-31')
print(f"Generated {len(month_ends)} month-end dates:")
print(month_ends)

# Find all CSV files in current directory (adjust pattern as needed)
csv_files = glob.glob("*.csv")
if not csv_files:
    print("No CSV files found. Please ensure CSV files are in the current directory.")
else:
    print(f"\nFound {len(csv_files)} CSV files: {csv_files}")
    
    # Process each CSV file
    all_results = {}
    
    for file_path in csv_files:
        print(f"\nProcessing {file_path}...")
        
        # Read CSV (adjust column names if different)
        try:
            df = pd.read_csv(file_path)
            
            # Convert date column to datetime (common names - adjust if needed)
            date_col = None
            for col in ['Date', 'date', 'DATE']:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col is None:
                print(f"  No date column found in {file_path}. Skipping...")
                continue
            
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.sort_values(date_col).reset_index(drop=True)
            
            # Filter for month-end dates (closest date to each month-end)
            results = []
            for month_end in month_ends:
                # Find closest date to month-end
                closest_idx = (df[date_col] - month_end).abs().idxmin()
                closest_date = df.loc[closest_idx, date_col]
                total_return = df.loc[closest_idx, 'Total Returns Index']
                
                results.append({
                    'Month_End': month_end.strftime('%Y-%m-%d'),
                    'Closest_Date': closest_date.strftime('%Y-%m-%d'),
                    'Total_Returns_Index': total_return
                })
            
            file_results_df = pd.DataFrame(results)
            all_results[file_path] = file_results_df
            
            print(f"  Processed {len(results)} dates successfully.")
            
        except Exception as e:
            print(f"  Error processing {file_path}: {str(e)}")
    
    # Save results
    if all_results:
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        
        # Individual files
        for file_name, result_df in all_results.items():
            base_name = os.path.splitext(os.path.basename(file_name))[0]
            output_file = f"{output_dir}/{base_name}_monthend_returns.csv"
            result_df.to_csv(output_file, index=False)
            print(f"Saved: {output_file}")
        
        # Combined file
        combined_df = pd.concat(all_results.values(), keys=all_results.keys())
        combined_df.to_csv(f"{output_dir}/all_monthend_returns.csv")
        print(f"Saved combined results: {output_dir}/all_monthend_returns.csv")
        
        print("\nPreview of first file:")
        print(all_results[list(all_results.keys())[0]].head())