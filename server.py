import os
from src.config.app import aplicacao

# INICIALIZAR O SERVIDOR
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    print('******** SERVIDOR DA APLICACAO NO AR!! ********')
    aplicacao.run(host='0.0.0.0', port=3000, debug=debug_mode)

