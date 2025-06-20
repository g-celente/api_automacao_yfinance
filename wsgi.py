from app import create_app
import os

# Cria a instância da aplicação
app = create_app('development')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
