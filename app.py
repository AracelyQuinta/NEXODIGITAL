from flask import Flask, render_template

app = Flask(__name__)


# Ruta principal (pagina informativa)
@app.route('/')
def inicio():
    return render_template('index.html')


# Modulo de Servicios
@app.route('/servicios')
def servicios():
    return render_template('servicios.html')


# Modulo de Proveedores
@app.route('/proveedores')
def proveedores():
    return render_template('proveedores.html')


# Modulo de Clientes
@app.route('/clientes')
def clientes():
    return render_template('clientes.html')


# Modulo de Facturacion
@app.route('/facturacion')
def facturacion():
    return render_template('facturacion.html')


# Punto de entrada
if __name__ == '__main__':
    app.run(debug=True)