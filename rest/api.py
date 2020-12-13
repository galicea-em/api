from flask_restx import Api
from conf import app

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
}

api = Api(app,
    endpoint="/",
    version='1.0',
    title='API Server',
    description='OAuth / OpenId',
    doc='/help/',
    security='Bearer Auth', authorizations=authorizations
)
