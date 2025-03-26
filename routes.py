# Este archivo almacena las rutas de nuestra aplicación

from flask import Flask, render_template, request, redirect, url_for, make_response
from methods import crear_cuenta, iniciar_sesion, encontrar_usuario_id, agregar_tarea, actualizar_tarea, eliminar_tarea, obtener_tareas
from flask_jwt_extended import decode_token, verify_jwt_in_request, get_jwt_identity
from models import Task  # Import the Task class from the models module
from extensions import db_s  # Import the database session object

# Firma utilizada para firmar y verificar tokens JWT
firma = 'cvVElgt1FXxAIgLKrm0y07oWcO1L76'

def cargar_rutas(app):
    # Ruta principal que verifica si el usuario está autenticado y muestra la página de inicio
    @app.route('/')
    def pagina():
        logged = False  # Variable para controlar si el usuario está autenticado

        try:
            verify_jwt_in_request()  # Verifica si hay un JWT válido en la cookie
            logged = True  # Si el JWT es válido, el usuario está autenticado
        except Exception as e:
            logged = False  # Si hay una excepción, el usuario no está autenticado
            print(e)

        # Renderiza la página principal con la variable de estado de autenticación
        return render_template('index.html', logged=logged)


    # Ruta para mostrar la página de inicio de sesión con un mensaje de estado opcional
    @app.route('/login')
    def login():
        resultado = request.args.get('status')  # Obtiene el estado del intento de inicio de sesión
        return render_template('login.html', estado=resultado)
    

    # Ruta para mostrar la página de registro con un mensaje de estado opcional
    @app.route('/signup')
    def signup():
        resultado = request.args.get('status')  # Obtiene el estado del intento de registro
        return render_template('signup.html', estado=resultado)
    

    # Ruta para procesar los datos del formulario de inicio de sesión
    @app.route('/manipulacion', methods=['POST'])
    def manipular_datos():
        # Obtiene el correo y la contraseña del formulario
        correo = request.form.get('email')
        password = request.form.get('password')
        print(f'Correo: {correo}\nContraseña: {password}')

        # Llama a la función para iniciar sesión y verifica la respuesta
        respuesta_login = iniciar_sesion(correo, password)

        if respuesta_login['status'] == 'error':
            # Si hay un error, redirige a la página de inicio de sesión con el estado de error
            return redirect(url_for('login', status=respuesta_login['status']))

        # Si el inicio de sesión es exitoso, crea una respuesta con un token en la cookie
        respuesta = make_response(redirect(url_for('pagina')))
        respuesta.set_cookie('access_token_cookie', respuesta_login['token'], secure=True, httponly=True, max_age=180)
        return respuesta


    # Ruta para procesar los datos del formulario de creación de cuenta
    @app.route('/datos_crear_cuenta', methods=['POST'])
    def obtener_datos_cuenta():
        # Obtiene los datos del formulario
        nombre = request.form.get('name')
        correo = request.form.get('email')
        password = request.form.get('password')
        print(f'Nombre: {nombre}\nCorreo: {correo}\nPassword: {password}')

        # Llama a la función para crear una cuenta y verifica la respuesta
        respuesta_signup = crear_cuenta(nombre, correo, password)
        print(respuesta_signup)

        if respuesta_signup['status'] == 'error':
            # Si hay un error, redirige a la página de registro con el estado de error
            return redirect(url_for('signup', status=respuesta_signup['status']))

        # Si la cuenta se crea correctamente, redirige a la página principal
        return redirect(url_for('pagina', status=respuesta_signup['status']))


    # Ruta para mostrar una página de error
    @app.route('/error')
    def pantalla_error():
        return render_template('error.html')
    

     # Ruta para mostrar la información del usuario si está autenticado
    @app.route('/usuario')
    def pantalla_usuario():
        try:
            verify_jwt_in_request()  # Verifica que el token JWT sea válido
            usuario_actual = get_jwt_identity()  # Obtiene la identidad del usuario desde el token
            print(f"Usuario autenticado: {usuario_actual}")
            return render_template('user.html', nombre=usuario_actual)  # Muestra la página de usuario
        except Exception as e:
            print(f'Error al verificar JWT: {str(e)}')
            return redirect(url_for('login'))  # Si hay un error, redirige a la página de inicio de sesión


    # Ruta para cerrar sesión
    @app.route('/logout')
    def cerrar_sesion():
        respuesta = make_response(redirect(url_for('pagina')))
        respuesta.set_cookie('access_token_cookie', '')  # Elimina la cookie del token JWT
        return respuesta

    # Ruta para obtener información del usuario autenticado
    @app.route('/user_info')
    def obtener_info_usuario():
        try:
            verify_jwt_in_request()  # Verifica si el token JWT es válido
            user_token = request.cookies.get('access_token_cookie')  # Obtiene el token desde la cookie
            token_info = decode_token(user_token)  # Decodifica el token para obtener la información del usuario
            id_usuario = token_info['user_id']

            # Redirige a la página del usuario con el ID obtenido
            return redirect(url_for('pantalla_usuario', user_id=id_usuario))
        except Exception as e:
            print(e)
            return redirect(url_for('pagina'))  # Si hay un error, redirige a la página principal
        

    # Ruta para agregar una tarea
    @app.route('/tasks', methods=['POST'])
    def agregar_tarea():
         try:
            # Verificar el token
            verify_jwt_in_request()
            token_info = get_jwt_identity()
            name = request.form.get('name')
            description = request.form.get('description')
            status = request.form.get('status')

            if not name or not description:
                return {'status': 'error', 'error': 'Faltan campos'}
            
            #Crear una nueva tarea
            nueva_tarea = Task(name=name, description=description, status=status)
            db_s.session.add(nueva_tarea)
            db_s.session.commit()
         except Exception as e:
            print(f"Error al agregar tarea: {e}")
            return {'status': 'error', 'error': 'Error interno'}
        
         return redirect(url_for('pagina'))

    # Ruta para actualizar una tarea
    @app.route('/tasks/<int:task_id>/update', methods=['POST'])
    def actualizar_tarea(task_id):
        status = request.form.get('status')
        tarea = Task.query.get(task_id)
        if tarea:
            tarea.status = status
            db_s.session.commit()
        return redirect(url_for('pagina'))

    # Ruta para eliminar una tarea
    @app.route('/tasks/<int:task_id>/delete', methods=['POST'])
    def eliminar_tarea(task_id):
        tarea = Task.query.get(task_id)
        if tarea:
            db_s.session.delete(tarea)
            db_s.session.commit()
        return redirect(url_for('pagina'))

    # Ruta para obtener todas las tareas@app.route('/tasks', methods=['GET', 'POST'])
    @app.route('/tasks', methods=['GET', 'POST'])
    def manejar_tareas():
        if request.method == 'POST':
            try:
                # Verificar el token
                verify_jwt_in_request()
                token_info = get_jwt_identity()
                name = request.form.get('name')
                description = request.form.get('description')
                status = request.form.get('status')

                if not name or not description:
                    return {'status': 'error', 'error': 'Faltan campos'}
                
                #Crear una nueva tarea
                nueva_tarea = Task(name=name, description=description, status=status)
                db_s.session.add(nueva_tarea)
                db_s.session.commit()
            except Exception as e:
                print(f"Error al agregar tarea: {e}")
                return {'status': 'error', 'error': 'Error interno'}
            
            return redirect(url_for('pagina'))
        else:  # GET
            try:
                verify_jwt_in_request()
                # Obtener y mostrar las tareas
                tareas = Task.query.all()
                return render_template('tasks.html', tareas=tareas)
            except Exception as e:
                print(f"Error al obtener tareas: {e}")
                return redirect(url_for('pagina'))