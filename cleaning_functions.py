import pandas as pd

def load_and_clean_calendar(file_path):
    """
    Load and clean the calendar data by removing symbols and converting prices to numeric values.
    """
    # Load the CSV file into a DataFrame
    df_calendar = pd.read_csv(file_path)
    
    # Remove dollar signs and commas from 'price' and convert to numeric values
    df_calendar['price_numeric'] = df_calendar['price'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    
    # Return the cleaned DataFrame
    return df_calendar

def calculate_mean_price(df_calendar):
    """
    Calculate the mean price for each listing_id.
    """
    # Group by 'listing_id' and calculate the mean of 'price_numeric'
    return df_calendar.groupby('listing_id')['price_numeric'].mean().reset_index(name='base_price')

def load_and_clean_listings(file_path, select_columns):
    """
    Load the listings data, select relevant columns, and rename 'id' to 'listing_id'.
    """
    # Load the CSV file into a DataFrame
    df_listing = pd.read_csv(file_path)
    
    # Select only the columns of interest
    df_listing_clean = df_listing[select_columns]
    
    # Rename 'id' column to 'listing_id'
    df_listing_clean = df_listing_clean.rename(columns={'id': 'listing_id'})
    
    # Return the cleaned DataFrame
    return df_listing_clean

def merge_with_average_price(df_listing_clean, df_calendar_mean_price):
    """
    Merge cleaned listings data with the average price data and handle missing values.
    """
    # Merge listings data with average price data on 'listing_id'
    df_listing_clean_price = df_listing_clean.merge(df_calendar_mean_price[['listing_id', 'base_price']], 
                                                    on='listing_id', how='left')
    
    # Fill missing values with 'Unknown'
    df_listing_clean_price = df_listing_clean_price.fillna('Unknown')
    
    # Convert 'base_price' to numeric, coercing errors (non-numeric values)
    df_listing_clean_price['base_price'] = pd.to_numeric(df_listing_clean_price['base_price'], errors='coerce')
    
    # Fill any remaining missing values in 'base_price' with 'Unknown'
    df_listing_clean_price['base_price'] = df_listing_clean_price['base_price'].fillna('Unknown')
    
    # Convert 'base_price' to integers where possible, leave 'Unknown' as is
    df_listing_clean_price['base_price'] = df_listing_clean_price['base_price'].apply(lambda x: int(x) if isinstance(x, float) else x)
    
    # Return the merged DataFrame with cleaned prices
    return df_listing_clean_price

def set_display_options():
    """
    Configure pandas to display up to 200 rows and all columns.
    """
    # Set the maximum number of rows displayed to 200
    pd.set_option('display.max_rows', 200)
    
    # Show all columns in the DataFrame display
    pd.set_option('display.max_columns', None)

def save_to_csv(df, file_path):
    """
    Save the DataFrame to a CSV file.
    """
    # Save the DataFrame to a CSV file without the index
    df.to_csv(file_path, index=False)
