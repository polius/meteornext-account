from flask import Blueprint

class Health:
    def __init__(self, sql):
        self._sql = sql

    def blueprint(self):
        # Init blueprint
        health_blueprint = Blueprint('health', __name__, template_folder='health')

        @health_blueprint.route('/health', methods=['GET'])
        def health_method():
            self._sql.execute('SELECT 1')
            return ''

        return health_blueprint
