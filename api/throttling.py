from rest_framework.throttling import UserRateThrottle

class CustomUserRateThrottle(UserRateThrottle):
    rate = '10/hour'  # Ограничение на 10 запросов в час для каждого пользователя

class CustomAnonRateThrottle(UserRateThrottle):
    rate = '5/hour'  # Ограничение на 5 запросов в час для анонимных пользователей