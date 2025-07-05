class BusinessLogicError(Exception):
    """
    自定义业务逻辑异常。
    用于在 Service 层或 View 层中主动抛出预期的错误。
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
