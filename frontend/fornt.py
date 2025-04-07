from fastapi import FastAPI, Request, HTTPException
import httpx
import os
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
import json

load_dotenv()
app = FastAPI()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/auth/callback"

# Step 1: Redirect to Google login
@app.get("/login")
def login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(google_auth_url)

# Step 2: Handle Google redirect and exchange code for token
@app.get("/auth/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")
    
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            tokens = token_response.json()
            
            # Verify the ID token
            id_token = tokens.get("id_token")
            if not id_token:
                raise HTTPException(status_code=400, detail="ID token not found in response")
            
            # Get user info from Google
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {tokens.get('access_token')}"}
            )
            userinfo_response.raise_for_status()
            user_info = userinfo_response.json()
            
            return {
                "id_token": id_token,
                "access_token": tokens.get("access_token"),
                "user_info": user_info
            }
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Failed to exchange code for token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add a new endpoint to verify tokens from the frontend
@app.post("/verify-token")
async def verify_token(request: Request):
    try:
        data = await request.json()
        token = data.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="Token not provided")
            
        async with httpx.AsyncClient() as client:
            # Verify the token with Google
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/tokeninfo",
                params={"id_token": token}
            )
            response.raise_for_status()
            token_info = response.json()
            
            # Verify the token was issued to our client
            if token_info.get("aud") != CLIENT_ID:
                raise HTTPException(status_code=400, detail="Invalid token audience")
                
            return token_info
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Failed to verify token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
