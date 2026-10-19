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
        "url": "https://fakestoreapi.com/products",
        "link": "https://fakestoreapi.com/",
        "description": "A free REST API for e-commerce testing. Falls back to a local model if servers drop."
    },
    "Platzi Fake Store API": {
        "url": "https://api.escuelajs.co/api/v1/products",
        "link": "https://fakeapi.platzi.com/",
        "description": "Real fashion product database. Falls back to a local model if servers drop."
    }
}

# 3. Offline Hardcoded Sandbox Database (Failsafe Backup Layout)
OFFLINE_FAKESTORE_MOCK = [
    {"id": 101, "title": "Premium Denim Trucker Jacket", "price": 89.99, "category": "men's clothing", "description": "Classic fit washed cotton jean jacket with double stitching and iron rivets.", "image": "https://unsplash.com"},
    {"id": 102, "title": "Slim-Fit Vintage Oxford Shirt", "price": 45.00, "category": "men's clothing", "description": "Breathable 100% organic cotton weave ideal for business casual or summer layer sets.", "image": "https://unsplash.com"},
    {"id": 103, "title": "Urban Weatherproof Windbreaker", "price": 110.00, "category": "men's clothing", "description": "Matte finish technical nylon outer shield featuring seamless waterproof thermal zippers.", "image": "https://unsplash.com"}
]

OFFLINE_PLATZI_MOCK = [
    {"id": 201, "title": "Retro Canvas Low-Top Sneakers", "price": 65.50, "description": "Vulcanized heavy-duty rubber sole paired with reinforced stitch breathability profile.", "images": ["https://unsplash.com"]},
    {"id": 202, "title": "Boho A-Line Summer Sundress", "price": 75.00, "description": "Flowing silhouette print dress woven cleanly with custom linen-blend luxury straps.", "images": ["https://unsplash.com"]},
    {"id": 203, "title": "Minimalist Full-Grain Suede Tote", "price": 140.00, "description": "Spacious main structural chamber featuring modular leather zip inserts.", "images": ["https://unsplash.com"]}
]

# 4. Main Header
st.title("👗 Multi-API Digital Clothing Boutique")
st.write("Welcome to the aggregate clothing hub powered concurrently by independent free data platforms.")

# 5. API Directory Links Layout
st.markdown("### 🔗 Direct API Documentation Links")
api_cols = st.columns(2)
for idx, (name, info) in enumerate(API_SOURCES.items()):
    with api_cols[idx]:
        with st.container(border=True):
            st.markdown(f"#### **[{name}]({info['link']})**")
            st.write(info['description'])
            st.caption(f"Endpoint: `{info['url']}`")

st.markdown("---")

# 6. Navigation Control Elements
st.markdown("### 🗂️ Explore Collections")
app_mode = st.segmented_control(
    "Choose a Store Section:", 
    options=["All Clothing", "Fake Store API Inventory", "Platzi Fashion API Inventory"],
    default="All Clothing"
)

# 7. Resilient Data Fetchers with Direct Fallbacks
@st.cache_data(ttl=60)
def fetch_fake_store_data():
    try:
        res = requests.get("https://fakestoreapi.com/products", timeout=4)
        if res.status_code == 200 and len(res.json()) > 0:
            all_items = res.json()
            clothing = [i for i in all_items if i.get('category', '').lower() in ["men's clothing", "women's clothing"]]
            return clothing if clothing else all_items[:6]
    except Exception:
        pass
    return OFFLINE_FAKESTORE_MOCK  # Failover backup triggered safely

@st.cache_data(ttl=60)
def fetch_platzi_data():
    try:
        res = requests.get("https://api.escuelajs.co/api/v1/products", timeout=4)
        if res.status_code == 200 and len(res.json()) > 0:
            return res.json()[:6]
    except Exception:
        pass
    return OFFLINE_PLATZI_MOCK  # Failover backup triggered safely

# 8. Unpacking String Arrays Natively
def parse_image_url(images_field):
    if not images_field:
        return "https://unsplash.com"
    raw = images_field[0] if isinstance(images_field, list) else str(images_field)
    raw = raw.strip('[]"\' ')
    if "placeimg.com" in raw or not raw.startswith("http"):
        return "https://unsplash.com"
    return raw

# 9. UI Grid Layout Renderer
def render_product_grid(products, source_type):
    cols = st.columns(3)
    for i, item in enumerate(products):
        with cols[i % 3]:
            title = item.get('title', 'Premium Apparel')
            price = item.get('price', 0.0)
            desc = item.get('description', 'High-quality curated collection item.')[:85] + "..."
            
            image_url = parse_image_url(item.get('image' if source_type == "fakestore" else 'images'))

            with st.container(border=True):
                st.image(image_url, use_container_width=True)
                st.subheader(f"{title[:35]}")
                st.markdown(f"### **\${price}**")
                st.caption(desc)
                
                if st.button("Add to Cart", key=f"btn_{source_type}_{item.get('id', i)}"):
                    st.success("Added to cart!")

# 10. Load and Display Products
fake_store_products = fetch_fake_store_data()
platzi_products = fetch_platzi_data()

# Show feedback banners if local fallbacks are currently serving data
if fake_store_products == OFFLINE_FAKESTORE_MOCK or platzi_products == OFFLINE_PLATZI_MOCK:
    st.toast("⚠️ One or more remote API servers are offline. Displaying sandbox warehouse backup data.", icon="💡")

if app_mode == "All Clothing":
    st.markdown("### 🏷️ From: Fake Store API Section")
    render_product_grid(fake_store_products, "fakestore")
    st.markdown("---")
    st.markdown("### 🏷️ From: Platzi Fashion API Section")
    render_product_grid(platzi_products, "platzi")

elif app_mode == "Fake Store API Inventory":
    st.markdown("## 🛒 Fake Store API Feed")
    render_product_grid(fake_store_products, "fakestore")

elif app_mode == "Platzi Fashion API Inventory":
    st.markdown("## 👟 Platzi API Feed")
    render_product_grid(platzi_products, "platzi")
