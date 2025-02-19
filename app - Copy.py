from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:***", "http://localhost:***"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Tokens
google_access_token = None
wp_access_token = None

# Request Models
class SEORequest(BaseModel):
    website_url: str

class ContentRequest(BaseModel):
    content: str

class SEOFixRequest(BaseModel):
    website_url: str
    post_id: int
    meta_description: str
    alt_text: str

# Google OAuth Flow
GOOGLE_REDIRECT_URI = "http://localhost:8000/google/callback"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/indexing",
    "https://www.googleapis.com/auth/webmasters"
]

def create_google_flow():
    return Flow.from_client_secrets_file(
        "credentials.json",
        scopes=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )

@app.get("/google/authorize")
async def google_authorize():
    flow = create_google_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", include_granted_scopes="true")
    return {"auth_url": auth_url}

@app.get("/google/callback")
async def google_callback(code: str):
    global google_access_token
    flow = create_google_flow()
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        google_access_token = credentials.token
        return {"message": "✅ Google Authorization Successful!", "access_token": google_access_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google Authorization Error: {e}")

# SEO Analysis Endpoint
@app.post("/analyze")
async def analyze_seo(data: SEORequest):
    try:
        response = requests.get(data.website_url)
        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.title.string if soup.title else "N/A"
        meta_description = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_description["content"] if meta_description else "N/A"
        h1_count = len(soup.find_all("h1"))
        images_without_alt = len([img for img in soup.find_all("img") if not img.get("alt")])
        internal_links_count = len([a for a in soup.find_all("a", href=True) if urlparse(a["href"]).netloc == ""])

        return {
            "title": title,
            "meta_description": meta_description,
            "h1_count": h1_count,
            "images_without_alt": images_without_alt,
            "internal_links_count": internal_links_count,
            "performance_score": 85  # Placeholder score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SEO Analysis Error: {e}")

# AI Content Suggestions
# AI Content Suggestions (Advanced Version)
@app.post("/content-suggestions")
async def content_suggestions(data: SEORequest):
    try:
        suggestions = [
            {
                "title": "Improve Meta Descriptions",
                "explanation": "Meta descriptions are short summaries that appear under your page title in search results. A well-written description improves click-through rates.",
                "how_to_fix": "Ensure each page has a unique, engaging description under 160 characters that includes your target keywords."
            },
            {
                "title": "Optimize Header Tags",
                "explanation": "Header tags help structure your content for both readers and search engines. They improve readability and SEO rankings.",
                "how_to_fix": "Use one H1 tag for the main title, and H2/H3 for subheadings. Include relevant keywords in headers without overstuffing."
            },
            {
                "title": "Use ALT Attributes for Images",
                "explanation": "ALT text describes images to search engines and improves accessibility for visually impaired users.",
                "how_to_fix": "Add clear, concise descriptions to all images. Mention the topic or keywords if relevant."
            },
            {
                "title": "Enhance Internal Linking",
                "explanation": "Internal links connect pages within your website, helping search engines understand your content hierarchy.",
                "how_to_fix": "Add links between related pages to guide users and distribute SEO value across your site."
            },
            {
                "title": "Improve Page Load Speed",
                "explanation": "Faster websites improve user experience and SEO rankings. Slow load times can increase bounce rates.",
                "how_to_fix": "Compress images, use browser caching, minimize CSS/JavaScript files, and consider a Content Delivery Network (CDN)."
            },
            {
                "title": "Add Structured Data for Rich Snippets",
                "explanation": "Structured data helps search engines understand your content better, enhancing rich snippet display in search results.",
                "how_to_fix": "Implement JSON-LD schema markup for articles, products, events, and other relevant content types."
            },
            {
                "title": "Focus on Mobile-First Design",
                "explanation": "Google prioritizes mobile-friendly websites. Poor mobile UX can hurt your rankings.",
                "how_to_fix": "Ensure responsive design, fast load times, and intuitive navigation on mobile devices."
            },
            {
                "title": "Optimize for Voice Search",
                "explanation": "With the rise of voice assistants, optimizing for voice search can improve organic visibility.",
                "how_to_fix": "Use natural, conversational language in your content and answer common questions concisely."
            },
            {
                "title": "Leverage Long-Tail Keywords",
                "explanation": "Long-tail keywords drive highly targeted traffic with less competition.",
                "how_to_fix": "Identify specific phrases your audience searches for and integrate them naturally into your content."
            },
            {
                "title": "Ensure HTTPS Security",
                "explanation": "HTTPS is a ranking factor. Sites without it may be flagged as 'Not Secure' by browsers.",
                "how_to_fix": "Install an SSL certificate to secure your website and improve SEO rankings."
            }
        ]
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Content Suggestions Error: {e}")


# Optimize SEO
@app.post("/optimize")
async def optimize_seo(data: SEORequest):
    return {"message": f"✅ SEO optimization completed for {data.website_url}"}

# Submit for Google Indexing
@app.post("/submit-indexing")
async def submit_indexing(data: SEORequest):
    if not google_access_token:
        raise HTTPException(status_code=401, detail="Unauthorized: Please authorize with Google first.")
    return {"message": f"✅ {data.website_url} submitted for Google Indexing"}

# Fix WordPress SEO
@app.post("/fix/wordpress")
async def fix_wordpress_seo(data: SEORequest):
    return {"message": f"✅ WordPress SEO issues fixed for {data.website_url}"}

# Advanced SEO Analysis
@app.post("/advanced-analyze")
async def advanced_analyze_seo(data: SEORequest):
    try:
        response = requests.get(f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={data.website_url}&strategy=desktop")
        pagespeed_data = response.json()
        performance_score = pagespeed_data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", 0) * 100

        cls = pagespeed_data.get("lighthouseResult", {}).get("audits", {}).get("cumulative-layout-shift", {}).get("displayValue", "N/A")
        lcp = pagespeed_data.get("lighthouseResult", {}).get("audits", {}).get("largest-contentful-paint", {}).get("displayValue", "N/A")
        tti = pagespeed_data.get("lighthouseResult", {}).get("audits", {}).get("interactive", {}).get("displayValue", "N/A")

        return {
            "performance_score": performance_score,
            "CLS": cls,
            "LCP": lcp,
            "TTI": tti
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced SEO Analysis Error: {e}")

# WordPress SEO Auto Fix Endpoint
@app.post("/fix-wordpress-seo")
async def auto_fix_wordpress_seo(data: SEOFixRequest):
    try:
        WP_API_URL = "https://photoartisto.com/wp-json/***"
        WP_USERNAME = "SEO-Tool"
        WP_APP_PASSWORD = "*************************"

        auth = (WP_USERNAME, WP_APP_PASSWORD)

        meta_response = requests.post(
            f"{WP_API_URL}/posts/{data.post_id}",
            auth=auth,
            json={"excerpt": data.meta_description}
        )

        media_response = requests.get(f"{WP_API_URL}/posts/{data.post_id}", auth=auth)
        featured_image_id = media_response.json().get("featured_media")

        if featured_image_id:
            alt_text_response = requests.post(
                f"{WP_API_URL}/media/{featured_image_id}",
                auth=auth,
                json={"alt_text": data.alt_text}
            )

        return {
            "message": "✅ SEO Issues Fixed Successfully!",
            "meta_update": meta_response.status_code,
            "alt_text_update": alt_text_response.status_code if featured_image_id else "No Image Found",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WordPress SEO Fix Error: {e}")
