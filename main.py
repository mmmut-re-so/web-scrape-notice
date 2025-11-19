from notice_scrape import notice_scrape
from announcement_scrape import announcement_scrape
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/download")
def download_notice():
    try:
        data = notice_scrape()
        notices = data.get("notices", [])
        links = data.get("links_list", [])
        titles = data.get("link_titles", [])
        
        # Create a dictionary mapping titles to links (backward compatible)
        links_dict = {}
        for i in range(len(titles)):
            links_dict[titles[i]] = links[i]
            
        return {
            "status": "success",
            "count": len(notices),
            "notices": notices,  # New structured format with title and link
            "links": links_dict   # Backward compatible format
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

@app.get("/announcements")
def get_announcements():
    try:
        data = announcement_scrape()
        announcements = data.get("announcements", [])
            
        return {
            "status": "success",
            "count": len(announcements),
            "announcements": announcements,  # New structured format with title and link
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
