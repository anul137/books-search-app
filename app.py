import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Books to Scrape - Search Engine",
    page_icon="📚",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    data_path = Path("data/books.json")
    if data_path.exists():
        with open(data_path, 'r', encoding='utf-8') as f:
            books = json.load(f)
        return pd.DataFrame(books)
    else:
        st.error("Data file not found. Please run the scraper first.")
        return pd.DataFrame()

# Main app
def main():
    st.title("📚 Books to Scrape - Search Engine")
    st.markdown("Search and explore books from Books to Scrape website")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No data available. Please run the scraper first.")
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Category filter
    categories = ['All'] + sorted(df['category'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Select Category", categories)
    
    # Rating filter
    ratings = ['All'] + sorted(df['rating'].dropna().unique().tolist())
    selected_rating = st.sidebar.selectbox("Select Rating", ratings)
    
    # Price range filter
    if not df['price'].isna().all():
        price_values = df['price'].str.replace('£', '').astype(float)
        min_price = st.sidebar.slider("Minimum Price (£)", 
                                    min_value=float(price_values.min()), 
                                    max_value=float(price_values.max()),
                                    value=float(price_values.min()))
        max_price = st.sidebar.slider("Maximum Price (£)", 
                                    min_value=float(price_values.min()), 
                                    max_value=float(price_values.max()),
                                    value=float(price_values.max()))
    
    # Search box
    search_query = st.text_input("Search books by title or description", "")
    
    # Filter data
    filtered_df = df.copy()
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    if selected_rating != 'All':
        filtered_df = filtered_df[filtered_df['rating'] == selected_rating]
    
    if 'price' in filtered_df.columns:
        price_numeric = filtered_df['price'].str.replace('£', '').astype(float)
        filtered_df = filtered_df[(price_numeric >= min_price) & (price_numeric <= max_price)]
    
    if search_query:
        mask = (filtered_df['title'].str.contains(search_query, case=False, na=False) |
                filtered_df['description'].str.contains(search_query, case=False, na=False))
        filtered_df = filtered_df[mask]
    
    # Display results
    st.header(f"Found {len(filtered_df)} books")
    
    if not filtered_df.empty:
        # Display books in a grid
        cols = st.columns(3)
        for idx, (_, book) in enumerate(filtered_df.iterrows()):
            col = cols[idx % 3]
            
            with col:
                st.subheader(book['title'][:50] + "..." if len(book['title']) > 50 else book['title'])
                
                if book['image_url']:
                    st.image(book['image_url'], width=200)
                
                st.write(f"**Price:** {book['price']}")
                st.write(f"**Rating:** {book['rating']}")
                st.write(f"**Category:** {book['category']}")
                st.write(f"**Availability:** {book['availability']}")
                
                if book['description']:
                    description = book['description'][:100] + "..." if len(book['description']) > 100 else book['description']
                    st.write(f"**Description:** {description}")
                
                if book['url']:
                    st.markdown(f"[View Details]({book['url']})")
                
                st.divider()
    else:
        st.write("No books found matching your criteria.")
    
    # Statistics
    st.sidebar.header("Statistics")
    st.sidebar.write(f"Total Books: {len(df)}")
    st.sidebar.write(f"Categories: {df['category'].nunique()}")
    st.sidebar.write(f"Unique Ratings: {df['rating'].nunique()}")

if __name__ == "__main__":
    main()