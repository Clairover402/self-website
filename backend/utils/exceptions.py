"""
自定义异常模块

定义应用层的异常类层次结构。
所有业务异常继承自 AppException，由全局异常处理器统一捕获并转换为 Result.fail() 响应。

使用方式：
    raise NotFoundException("博客未找到", err_code="BLOG_NOT_FOUND")
    raise ConflictException("slug 已存在", err_code="SLUG_DUPLICATE")

相比在各路由中手动 return Result.fail()，抛出异常的优势：
- 路由代码更简洁，只需关注正常流程
- 错误处理逻辑集中管理，便于统一修改响应格式
- 异常可以跨多层传播，Service/CRUD 层也能安全使用
"""


class AppException(Exception):
    """
    应用层基础异常

    所有自定义业务异常的超类。
    全局异常处理器通过捕获此类统一处理所有业务错误。

    属性：
        message: 用户可读的错误描述
        err_code: 机器可读的错误码，方便前端做程序化处理
        status_code: HTTP 状态码（默认 400）
    """

    def __init__(
        self,
        message: str,
        err_code: str = "APP_ERROR",
        status_code: int = 400,
    ):
        self.message = message
        self.err_code = err_code
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """
    资源未找到异常

    用于表示数据库查询无结果等场景。
    默认 HTTP 状态码 404。

    使用示例：
        raise NotFoundException("博客未找到", err_code="BLOG_NOT_FOUND")
    """

    def __init__(self, message: str = "资源未找到", err_code: str = "NOT_FOUND"):
        super().__init__(message=message, err_code=err_code, status_code=404)


class ConflictException(AppException):
    """
    资源冲突异常

    用于表示创建或更新时的唯一性冲突（如重复 slug）。
    默认 HTTP 状态码 409。

    使用示例：
        raise ConflictException("slug 已存在", err_code="SLUG_DUPLICATE")
    """

    def __init__(self, message: str = "资源冲突", err_code: str = "CONFLICT"):
        super().__init__(message=message, err_code=err_code, status_code=409)


class ValidationException(AppException):
    """
    业务校验异常

    用于表示业务规则校验失败（非 Pydantic 的类型校验）。
    默认 HTTP 状态码 422。

    使用示例：
        raise ValidationException("read_time 不能为负数", err_code="INVALID_READ_TIME")
    """

    def __init__(self, message: str = "校验失败", err_code: str = "VALIDATION_ERROR"):
        super().__init__(message=message, err_code=err_code, status_code=422)
