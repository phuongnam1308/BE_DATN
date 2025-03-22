from fastapi import APIRouter, HTTPException
from models import CrawlRequest, CrawlResponse
from crawler import crawl_facebook_page
from database import create_tables, save_raw_to_db, save_clean_to_db

router = APIRouter()

@router.post("/crawl", response_model=CrawlResponse)
async def crawl_endpoint(request: CrawlRequest):
    try:
        # Tạo cả hai bảng nếu chưa có
        create_tables()
        
        # Crawl dữ liệu
        posts = crawl_facebook_page(request.url, request.target_posts)
        
        # Lưu dữ liệu thô vào raw_fanpage_facebook
        save_raw_to_db(posts)
        
        # Tiền xử lý và lưu vào clean_fanpage_facebook
        save_clean_to_db(posts, request.url)
        
        return {
            "url": request.url,
            "posts": posts,
            "message": f"Đã crawl, lưu {len(posts)} bài viết vào raw_fanpage_facebook và clean_fanpage_facebook!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi crawl: {str(e)}")