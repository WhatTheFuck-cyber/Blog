# 仅挂载为包

# 从各文件导入模型
from .minimal import UserMinimal, ArticleMinimal, CommentMinimal, ArticleMinimalWithStats
from .users import UserBase, UserCreate, User, UserLogin, UserSearch, UserInfo
from .articles import ArticleBase, ArticleCreate, ArticleUpdate, Article, ArticleWithStats
from .comments import CommentBase, CommentCreate, CommentUpdate, Comment
from .categories import CategoryBase, CategoryCreate, Category
from .token import TokenRefresh, LoginResponse
from .home import HomeResponse
from .messages import MessageBase, MessageCreate, Message, MessageDetail
from .interactions import LikeBase, LikeCreate, Like, CollectBase, CollectCreate, Collect



# 对外导出
__all__ = [
    # 用户相关
    "UserMinimal", "UserBase", "UserCreate", "User", "UserLogin", "UserSearch", "UserInfo"
    # 文章相关
    "ArticleMinimal", "ArticleBase", "ArticleCreate", "ArticleUpdate", "Article", "ArticleWithStats", "ArticleMinimalWithStats"
    # 评论相关
    "CommentMinimal", "CommentBase", "CommentCreate", "CommentUpdate", "Comment",
    # 分类相关
    "CategoryBase", "CategoryCreate", "Category",
    # 令牌相关
    "TokenRefresh", "LoginResponse",
    # 主页相关
    "HomeResponse",
    # 私信相关
    "MessageBase", "MessageCreate", "Message", "MessageDetail",
    # 互动相关
    "LikeBase", "LikeCreate", "Like", "CollectBase", "CollectCreate", "Collect"
]