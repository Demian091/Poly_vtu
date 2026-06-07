from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AnonBurstRateThrottle(AnonRateThrottle):
    """Strict rate limit for anonymous users"""
    scope = 'anon_burst'
    rate = '5/minute'


class AnonSustainedRateThrottle(AnonRateThrottle):
    """Sustained rate limit for anonymous users"""
    scope = 'anon_sustained'
    rate = '100/day'


class UserBurstRateThrottle(UserRateThrottle):
    """Burst rate limit for authenticated users"""
    scope = 'user_burst'
    rate = '60/minute'


class UserSustainedRateThrottle(UserRateThrottle):
    """Sustained rate limit for authenticated users"""
    scope = 'user_sustained'
    rate = '1000/day'
