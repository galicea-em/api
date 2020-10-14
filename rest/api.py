from flask_restx import Api
from conf import app

api = Api(app,
    endpoint="/",
    version='1.0',
    title='API Server',
    description='OAuth / OpenId / VM',
    doc='/help/'
)
