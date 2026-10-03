class NotifyCharacteristicNotFoundError(Exception):
    """
    Service discover error
    """
    pass

class ConnectionAttemptsExceededError(Exception):
    """ Connection attempts exceeded """
    pass

class NotificationSubscriptionError(Exception):
    """ Notification subscription error """
    pass
