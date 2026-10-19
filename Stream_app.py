import streamlit as st
import requests
import json

# 1. Page Configuration
st.set_page_config(
    page_title="Multi-API Clothing Store",
    page_icon="🛍️",
    layout="wide"
)

# 2. Define Free API Sources & Links
API_SOURCES = {
    "Fake Store API": {
        "url": "https://fakestoreapi.com",
        "link": "https://fakestoreapi.com",
        "description": "A free online REST API for e-commerce testing. We pull curated fashion items from here."
    },
    "Platzi Fake Store API": {
        "url": "https://escuelajs.co",
        "link": "https://platzi.com",
        "description": "Real e-commerce data with high-quality fashion product images and clean JSON outputs."
    }
}

# 3. Main Header & Banner
st.title("👗 Multi-API Digital Clothing Boutique")
st.write("Welcome to the aggregate clothing hub powered concurrently by independent free data platforms.")

# 4. API Directory Layout (Directly on the Home Page)
st.markdown("### 🔗 Direct API Documentation Links")
api_cols = st.columns(2)

for idx, (name, info) in enumerate(API_SOURCES.items()):
    with api_cols[idx]:
        with st.container(border=True):
            st.markdown(f"#### **[{name}]({info['link']})**")
            st.write(info['description'])
            st.caption(f"Endpoint: `{info['url']}`")

st.markdown("---")

# 5. Native Page Filter Selection
st.markdown("### 🗂️ Explore Collections")
app_mode = st.segmented_control(
    "Choose a Store Section:", 
    options=["All Clothing", "Fake Store API Inventory", "Platzi Fashion API Inventory"],
    default="All Clothing"
)

# 6. Data Fetching Functions
@st.cache_data(ttl=300)
def fetch_fake_store_data():
    try:
        res = requests.get("https://fakestoreapi.com", timeout=8)
        if res.status_code == 200:
            all_items = res.json()
            clothing = [
                item for item in all_items 
                if item.get('category', '').lower() in ["men's clothing", "women's clothing"]
            ]
            return clothing if clothing else all_items[:10]
        return []
    except Exception:
        return []

@st.cache_data(ttl=300)
def fetch_platzi_data():
    try:
        res = requests.get("https://escuelajs.co", timeout=8)
        if res.status_code == 200:
            all_items = res.json()
            clothing = [
                item for item in all_items
                if item.get('category', {}).get('name', '').lower() in ['clothes', 'shoes', 'miscellaneous']
            ]
            return clothing[:15] if clothing else all_items[:15]
        return []
    except Exception:
        return []

# 7. High-Res Working Production Unsplash CDN Image Fallback Dictionary
def get_reliable_cdn_fallback(text_context):
    text_lower = str(text_context).lower()
    
    # 100% stable, fixed production CDN links from Unsplash image database
    cdn_links = {
        "shoes": "https://unsplash.com",
        "sneakers": "https://unsplash.com",
        "jacket": "https://unsplash.com",
        "shirt": "https://unsplash.com",
        "jeans": "https://unsplash.com",
        "dress": "https://unsplash.com",
        "bag": "https://unsplash.com",
        "watch": "https://unsplash.com"
    }
    
    for key, url in cdn_links.items():
        if key in text_lower:
            return url
            
    # Default top fashion photo if no specific keyword matches
    return "https://unsplash.com"

# 8. Fast URL String Filter
def parse_image_url(images_field, product_context_text):
    fallback_image = get_reliable_cdn_fallback(product_context_text)
    
    if not images_field:
        return fallback_image
        
    raw_url = images_field if isinstance(images_field, list) else str(images_field)
    
    # Fast string unpacking
    for _ in range(3):
        raw_url = raw_url.strip('[]"\' ')
        if raw_url.startswith('["') or raw_url.startswith('['):
            try:
                parsed = json.loads(raw_url)
                raw_url = parsed if isinstance(parsed, list) else str(parsed)
            except:
                pass

    # Force fallback if the API serves broken test links
    if "placeimg.com" in raw_url or not raw_url.startswith("http") or "://unsplash.com" in raw_url:
        return fallback_image

    return raw_url

# 9. UI Grid Rendering Helper
def render_product_grid(products, source_type):
    if not products:
        st.info("No items available to display right now from this provider.")
        return

    cols = st.columns(3)
    for i, item in enumerate(products):
        with cols[i % 3]:
            title = item.get('title', 'Fashion Apparel')
            price = item.get('price', 0.0)
            desc = item.get('description', '')
            short_desc = desc[:90] + "..." if desc else "No product description provided."
            
            context_string = f"{title} {desc}"
            
            if source_type == "fakestore":
                image_url = parse_image_url(item.get('image'), context_string)
            else:
                image_url = parse_image_url(item.get('images'), context_string)

            with st.container(border=True):
                # Native fast loading without background network pre-checks
                st.image(image_url, use_container_width=True)
                st.subheader(f"{title[:35]}")
                st.markdown(f"### **\${price}**")
                st.caption(short_desc)
                
                if st.button("Add to Cart", key=f"btn_{source_type}_{item.get('id', i)}_{i}"):
                    st.success(f"Added item to cart!")

# 10. Rendering Content Grid
fake_store_products = fetch_fake_store_data()
platzi_products = fetch_platzi_data()

if app_mode == "All Clothing":
    st.markdown("### 🏷️ From: Fake Store API Section")
    render_product_grid(fake_store_products[:6], "fakestore")
    
    st.markdown("---")
    
    st.markdown("### 🏷️ From: Platzi Fashion API Section")
    render_product_grid(platzi_products[:6], "platzi")

elif app_mode == "Fake Store API Inventory":
    st.markdown("## 🛒 Fake Store API Exclusive Feed")
    render_product_grid(fake_store_products, "fakestore")

elif app_mode == "Platzi Fashion API Inventory":
    st.markdown("## 👟 Platzi API Exclusive Feed")
    render_product_grid(platzi_products, "platzi")
