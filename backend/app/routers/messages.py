# backend/app/routers/messages.py

from imports import APIRouter, Depends, HTTPException, Session
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user



router = APIRouter()



@router.post("", response_model=schemas.Message)
def send_message(
    message: schemas.MessageCreate,  # 此时接收的是receiver_email
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """发送私信（按邮箱发送，需要登录）"""
    try:
        # 1. 通过邮箱查询接收者（必须是活跃用户）
        receiver = db.query(models.User).filter(
            models.User.email == message.receiver_email,
            models.User.is_active == True
        ).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="接收用户不存在或已注销")
        
        # 2. 不能向自己发送私信
        if receiver.id == current_user.id:
            raise HTTPException(status_code=400, detail="不能向自己发送私信")
        
        # 3. 创建私信记录（使用查询到的接收者ID）
        db_message = models.Message(
            content=message.content,
            sender_id=current_user.id,
            receiver_id=receiver.id  # 存储的仍是用户ID
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        # 4. 构造响应（补充发送者邮箱信息）
        return {
            **db_message.__dict__,
            "sender_email": current_user.email,
            "receiver_email": message.receiver_email
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"发送私信失败：{str(e)}")



@router.get("/received", response_model=list[schemas.Message])
def get_received_messages(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取当前用户收到的所有私信（自动标记未读为已读）"""
    try:
        # 查询当前用户收到的私信（关联发送者信息）
        messages = db.query(models.Message)\
            .filter(models.Message.receiver_id == current_user.id)\
            .order_by(models.Message.created_at.desc())\
            .join(models.User, models.Message.sender_id == models.User.id)\
            .all()
        
        # 构造包含邮箱的响应数据（数据库模型没有邮箱字段，需手动补充）
        response_messages = []
        for msg in messages:
            response_messages.append({
                "id": msg.id,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "created_at": msg.created_at,
                "is_read": msg.is_read,
                "sender_email": msg.sender.email,  # 从关联的sender对象获取邮箱
                "receiver_email": current_user.email  # 接收者是当前用户，直接用其邮箱
            })
        
        return response_messages
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取收到的私信失败：{str(e)}")



@router.get("/sent", response_model=list[schemas.Message])
def get_sent_messages(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取当前用户发送的所有私信"""
    try:
        # 查询当前用户发送的私信（关联接收者信息）
        messages = db.query(models.Message)\
            .filter(models.Message.sender_id == current_user.id)\
            .order_by(models.Message.created_at.desc())\
            .join(models.User, models.Message.receiver_id == models.User.id)\
            .all()
        
        # 构造包含邮箱的响应数据
        response_messages = []
        for msg in messages:
            response_messages.append({
                "id": msg.id,
                "content": msg.content,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "created_at": msg.created_at,
                "is_read": msg.is_read,
                "sender_email": current_user.email,  # 发送者是当前用户，直接用其邮箱
                "receiver_email": msg.receiver.email  # 从关联的receiver对象获取邮箱
            })
        
        return response_messages
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取发送的私信失败：{str(e)}")



@router.get("/{message_id}", response_model=schemas.MessageDetail)
def get_message_detail(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取私信详情（只能查看自己发送或接收的私信）"""
    try:
        # 无需手动JOIN！模型中已定义sender/receiver关联，SQLAlchemy会自动处理
        message = db.query(models.Message).filter(models.Message.id == message_id).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="私信不存在")
        
        # 验证权限：只能查看自己发送或接收的私信
        if message.sender_id != current_user.id and message.receiver_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权查看此私信")
        
        # 如果是收到的未读消息，标记为已读
        if message.receiver_id == current_user.id and not message.is_read:
            message.is_read = True
            db.commit()
            db.refresh(message)  # 刷新对象，确保获取最新的is_read状态
        
        # 构造符合MessageDetail模型的响应数据
        # 1. 组装发送者极简信息（UserMinimal）- 直接从关联的sender对象获取
        sender_info = {
            "id": message.sender.id,
            "email": message.sender.email,
            "username": message.sender.username,  # 适配你的UserMinimal模型（无则删除）
            "is_active": message.sender.is_active
        }
        
        # 2. 组装接收者极简信息（UserMinimal）- 直接从关联的receiver对象获取
        receiver_info = {
            "id": message.receiver.id,
            "email": message.receiver.email,
            "username": message.receiver.username,  # 适配你的UserMinimal模型（无则删除）
            "is_active": message.receiver.is_active
        }
        
        # 3. 完整响应数据（覆盖MessageDetail所有字段）
        response_data = {
            "id": message.id,
            "content": message.content,
            "created_at": message.created_at,
            "is_read": message.is_read,
            "sender": sender_info,                     # 发送者完整信息
            "receiver": receiver_info                  # 接收者完整信息
        }
        
        return response_data
    except Exception as e:
        db.rollback()  # 异常时回滚事务
        raise HTTPException(status_code=500, detail=f"获取私信详情失败：{str(e)}")
    


@router.delete("/{message_id}", response_model=dict)
def recall_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """撤回私信（仅发送者可操作）"""
    try:
        # 1. 查询要撤回的私信
        message = db.query(models.Message).filter(models.Message.id == message_id).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="私信不存在")
        
        # 2. 验证权限：只有发送者可以撤回
        if message.sender_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权撤回此私信")
        
        # 3. 执行撤回（物理删除）
        db.delete(message)
        db.commit()
        
        return {"detail": "私信已成功撤回"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"撤回私信失败：{str(e)}")