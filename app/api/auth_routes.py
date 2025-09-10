from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.utils.auth import verify_web_password
from app.utils.logging import log
import app.config.settings as settings

# 创建认证路由器
auth_router = APIRouter(prefix="/api/auth", tags=["认证"])

# 登录请求模型
class LoginRequest(BaseModel):
    password: str

# 登录响应模型
class LoginResponse(BaseModel):
    success: bool
    message: str

@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request):
    """
    用户登录验证接口
    """
    try:
        # 获取客户端IP
        client_ip = req.client.host
        
        # 验证密码
        if not request.password:
            log("warning", f"登录失败：密码为空 - IP: {client_ip}")
            raise HTTPException(status_code=400, detail="密码不能为空")
        
        # 使用PASSWORD进行验证
        if request.password == settings.PASSWORD:
            log("info", f"用户登录成功 - IP: {client_ip}")
            return JSONResponse(content={"success": True, "message": "登录成功", "redirect": "/dashboard"})
        else:
            log("warning", f"登录失败：密码错误 - IP: {client_ip}")
            raise HTTPException(status_code=401, detail="密码错误")
            
    except HTTPException:
        raise
    except Exception as e:
        log("error", f"登录验证异常 - IP: {client_ip}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@auth_router.post("/logout")
async def logout(req: Request):
    """
    用户登出接口
    """
    try:
        client_ip = req.client.host
        log("info", f"用户登出 - IP: {client_ip}")
        return JSONResponse(content={"success": True, "message": "登出成功"})
    except Exception as e:
        log("error", f"登出异常 - IP: {client_ip}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@auth_router.get("/status")
async def get_auth_status():
    """
    获取认证配置状态
    """
    return JSONResponse(content={
        "password_required": bool(settings.PASSWORD),
        "web_password_set": bool(settings.WEB_PASSWORD and settings.WEB_PASSWORD != settings.PASSWORD)
    })