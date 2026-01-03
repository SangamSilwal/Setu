from fastapi import APIRouter , HTTPException , Depends , status
from schemas.user import UserCreate, Userlogin , Token
from core.security import hash_password , verify_password , create_access_token
from db.mongodb import get_database

router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db = Depends(get_database)):
    
    # 1. Check if user exists
    user_exists = await db["users"].find_one({'email': user_in.email})
    if user_exists:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # 2. Convert Pydantic model to dict
    user_dict = user_in.model_dump()

    # 3. Replace plain password with hashed password
    user_dict["password"] = hash_password(user_in.password)

    # 4. Insert into MongoDB
    result = await db["users"].insert_one(user_dict)
    
    # 5. Create access token for auto-login
    access_token = create_access_token(data={"sub": user_in.email})
    
    # 6. Prepare user data for response (remove password)
    user_response = {k: v for k, v in user_dict.items() if k != "password"}
    user_response["_id"] = str(result.inserted_id)
    
    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.post("/login",response_model=Token)
async def login(user_in:Userlogin,db= Depends(get_database)):
    ## Finding the  user 
    user = await db["users"].find_one({"email":user_in.email})

    ## Verifying the password 
    if not user or not verify_password(user_in.password,user["password"]):
        raise HTTPException(status_code=401,detail="Incorrect email or password")
    
    ##Create Token 
    access_token = create_access_token(data={"sub":user["email"]})
    return {"access_token":access_token,"token_type": "bearer"}

@router.get("/me")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """Get current logged-in user's information"""
    return current_user