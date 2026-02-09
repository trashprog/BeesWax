#version 1.04??????????????

# run  uvicorn main:app --host 0.0.0.0 --port 5000 for testing
import uvicorn
from fastapi import Depends, HTTPException, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware


from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime
import os
from fastapi.security import HTTPAuthorizationCredentials
from dotenv import load_dotenv
from auth_fastapi import init_auth
from utils import (
    hashDomain, 
    update_date,
    get_user_id)
from classes import RateCouponRequest, AddCouponRequest
from auth_fastapi import security
load_dotenv()



# app = Flask(__name__)
app = FastAPI()
# CORS(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.getenv("connection_string")) # found in environment variables. use ('127.0.0.1' , 27017) or other if running locally
db = client["coupons_db"]
coll = db["coupons"]

# login route imported
app.include_router(init_auth(db))

@app.get("/check_website")
async def check_website(hashedDomain: str = Query(..., description="Hashed website domain")):
    coupons = list(coll.find({"hash": hashedDomain, "hidden": {"$ne": True}}, {"_id": 1, "website": 1 , "code": 1, "rating": 1, "desc": 1 , "expiryDate": 1}))

    for coupon in coupons:
        coupon["_id"] = str(coupon["_id"])
        if "expiryDate" not in coupon:
            coupon["expiryDate"] = None
            coupon["expiresIn"] = None
        else:
            coupon['expiresIn'] = (datetime.strptime(coupon['expiryDate'] , "%Y-%m-%d") - datetime.now()).days
        
    return {"success": True, "coupons": coupons}

@app.post("/update")
async def update():
    for coupon in coll.find():
        new = update_date(coupon)
        coll.update_one({'_id': coupon['_id']}, {'$set': {'hidden': new['hidden']}})
    return {"success": True, "message": "Coupons updated."}

@app.post("/add_coupon")
async def add_coupon(
    data: AddCouponRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    token = credentials.credentials
    user_id = get_user_id(token) if token else None

    coupon = {
        "website": data.website,
        "code": data.coupon,
        "rating": 0,
        "desc": data.desc,
        "hash": hashDomain(data.website),
        "user_id": user_id,
    }

    if data.type == "expires":
        coupon["expiryDate"] = data.expiryDate
    elif data.type == "seasonal":
        coupon["expiryDate"] = data.expiryDate
        coupon["startDate"] = data.startDate

    result = coll.insert_one(coupon)

    return {
        "success": True,
        "coupon_id": str(result.inserted_id),
    }


@app.post("/rate_coupon")
async def rate_coupon(
    data: RateCouponRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    token = credentials.credentials
    user_id = get_user_id(token) if token else None

    try:
        coupon = coll.find_one({"_id": ObjectId(data.coupon_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid coupon_id")

    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")

    if user_id and user_id in coupon.get("rated_by", []):
        raise HTTPException(status_code=403, detail="Already rated")

    new_rating = coupon.get("rating", 0) + data.rating_change
    update_fields = {"rating": new_rating}

    if new_rating < 0:
        update_fields["hidden"] = True

    if user_id:
        update_fields["rated_by"] = coupon.get("rated_by", []) + [user_id]

    coll.update_one(
        {"_id": ObjectId(data.coupon_id)},
        {"$set": update_fields},
    )

    return {
        "success": True,
        "deleted": new_rating < 0,
    }
    

@app.get("/display_data", include_in_schema=False) # fyi before using: its ugly
def display():
     return dumps(list(coll.find()))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
    )
