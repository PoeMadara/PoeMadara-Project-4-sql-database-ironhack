import pandas as pd

def load_and_clean_calendar(file_path):
    """
    Load and clean the calendar data by removing symbols and converting prices to numeric values.
    """
    df_calendar = pd.read_csv(file_path)
    df_calendar['price_numeric'] = df_calendar['price'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    return df_calendar

def calculate_mean_price(df_calendar):
    """
    Calculate the mean price for each listing_id.
    """
    return df_calendar.groupby('listing_id')['price_numeric'].mean().reset_index(name='base_price')

def load_and_clean_listings(file_path, select_columns):
    """
    Load the listings data, select relevant columns, and rename 'id' to 'listing_id'.
    """
    df_listing = pd.read_csv(file_path)
    df_listing_clean = df_listing[select_columns]
    df_listing_clean = df_listing_clean.rename(columns={'id': 'listing_id'})
    return df_listing_clean

def merge_with_average_price(df_listing_clean, df_calendar_mean_price):
    """
    Merge cleaned listings data with the average price data and handle missing values.
    """
    df_listing_clean_price = df_listing_clean.merge(df_calendar_mean_price[['listing_id', 'base_price']], on='listing_id', how='left')
    df_listing_clean_price = df_listing_clean_price.fillna('Unknown')
    df_listing_clean_price['base_price'] = pd.to_numeric(df_listing_clean_price['base_price'], errors='coerce')
    df_listing_clean_price['base_price'] = df_listing_clean_price['base_price'].fillna('Unknown')
    df_listing_clean_price['base_price'] = df_listing_clean_price['base_price'].apply(lambda x: int(x) if isinstance(x, float) else x)
    return df_listing_clean_price

def set_display_options():
    """
    Configure pandas to display up to 10 rows and all columns.
    """
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.max_columns', None)

def save_to_csv(df, file_path):
    """
    Save the DataFrame to a CSV file.
    """
    df.to_csv(file_path, index=False)

# New functions from the third file
def create_civitatis_airbnb_listing(df_listing_clean_price):
    """
    Create the 'civitatis_airbnb_listing' table without index.
    """
    listing_columns = ['listing_id', 'host_id', 'longitude', 'latitude', 'room_type', 
                       'accommodates', 'instant_bookable', 'base_price']
    civitatis_airbnb_listing = df_listing_clean_price[listing_columns].copy(deep=True)
    civitatis_airbnb_listing.reset_index(drop=True, inplace=True)
    return civitatis_airbnb_listing

def create_civitatis_airbnb_reviews(df_listing_clean_price):
    """
    Create the 'civitatis_airbnb_reviews' table without index.
    """
    reviews_columns = ['listing_id', 'number_of_reviews', 'number_of_reviews_ltm', 'number_of_reviews_l30d', 'review_scores_rating']
    civitatis_airbnb_reviews = df_listing_clean_price[reviews_columns].copy(deep=True)
    civitatis_airbnb_reviews.rename(columns={
        'number_of_reviews_ltm': 'reviews_lastyear',
        'number_of_reviews_l30d': 'reviews_last30days'
    }, inplace=True)
    civitatis_airbnb_reviews['reviews_id'] = range(len(civitatis_airbnb_reviews))
    cols = ['reviews_id'] + [col for col in civitatis_airbnb_reviews.columns if col != 'reviews_id']
    civitatis_airbnb_reviews = civitatis_airbnb_reviews[cols]
    civitatis_airbnb_reviews.reset_index(drop=True, inplace=True)
    return civitatis_airbnb_reviews

def create_civitatis_airbnb_host(df_listing_clean_price):
    """
    Create the 'civitatis_airbnb_host' table and remove duplicates.
    """
    host_columns = ['host_id', 'host_name', 'host_since', 'host_location', 
                    'host_response_time', 'host_is_superhost', 'host_listings_count']
    civitatis_airbnb_host = df_listing_clean_price[host_columns].drop_duplicates(subset='host_id').copy(deep=True)
    civitatis_airbnb_host.reset_index(drop=True, inplace=True)
    return civitatis_airbnb_host

def export_tables_to_csv(civitatis_airbnb_listing, civitatis_airbnb_reviews, civitatis_airbnb_host):
    """
    Export the tables to CSV.
    """
    civitatis_airbnb_listing.to_csv('civitatis_airbnb_listing.csv', index=False)
    civitatis_airbnb_reviews.to_csv('civitatis_airbnb_reviews.csv', index=False)
    civitatis_airbnb_host.to_csv('civitatis_airbnb_host.csv', index=False)