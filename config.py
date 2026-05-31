

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Vjzs3455@localhost/mechanic_shop'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT: 300


class TestingConfig:
    pass

class ProductionConfig:
    pass

