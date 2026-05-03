📋 Requisitos previos
Antes de comenzar, asegúrate de tener:

Una cuenta en GitHub (gratuita)

Una cuenta en Render.com (puedes registrarte con GitHub)

Tu proyecto funcionando localmente

🚀 Paso 1: Preparar los archivos para producción

Asegúrate de que tu proyecto tenga esta estructura exacta:

Team-Starblack-Netflix/

├── app.py                 # Tu aplicación Flask

├── requirements.txt       # Dependencias de Python

├── Procfile               # ¡IMPORTANTE! Comando de inicio

├── users.txt              # Se creará automáticamente

├── templates/login.html, register.html, index.html.

└── static/style.css, login.css, register.css
    

🚀 Paso 2: Subir el código a GitHub

este paso no explico porque si leer esto ya sabe como hacerlo


🚀 Paso 3: Desplegar en Render

3.1 Crear el Web Service
Inicia sesión en render.com (usa "Sign in with GitHub")

Haz clic en "New +" → "Web Service" 

Conecta tu repositorio de GitHub:

Si es la primera vez, autoriza a Render a acceder a tus repos

Busca y selecciona Team-Starblack-Netflix


3.2 Configurar el servicio
Completa el formulario con estos valores:

Campo	Valor

Name : Team-Starblack-Netflix (o el nombre que quieras)

Root Directory : Déjalo vacío (tu proyecto está en la raíz)

Environment : Python 3 

Build Command : pip install -r requirements.txt

Start Command : gunicorn app:app


3.3 Seleccionar el plan gratuito
En la sección "Instance Type":

Selecciona "Free" 

ℹ️ Info del plan gratuito:

El servicio se duerme después de 15 minutos sin actividad 

Se despierta automáticamente cuando alguien visita la URL

La primera visita después de inactividad puede tardar 15-30 segundos

750 horas de uso al mes (más que suficiente)

 3.4 ¡Crear!
Haz clic en "Create Web Service" 🚀

Render comenzará a construir tu aplicación. Verás los logs en tiempo real.

🔍 Paso 4: Verificar el despliegue
✅ Si todo sale bien:
Verás Live en estado del servicio

Recibirás una URL como: https://Team-Starblack-Netflix.onrender.com

Accede a https://TU-APP.onrender.com/login


📞 Credenciales por defecto
Una vez desplegado, usa estas credenciales para probar:

Usuario     Contraseña

admin:admin123

demo:demo123

Los nuevos usuarios pueden registrarse en /register.


<img width="661" height="604" alt="image" src="https://github.com/user-attachments/assets/6628c5ca-e560-4b86-a53a-74fd8ddec2a0" />


como funciona 

debe carga la cookies y dar generar

<img width="1074" height="606" alt="image" src="https://github.com/user-attachments/assets/2fd1f466-8ce6-4a66-a324-658ed378f8d7" />
<img width="1085" height="610" alt="image" src="https://github.com/user-attachments/assets/f249bdb8-2d0e-4dbd-a87b-c182bd974892" />


el link lo pega en un navegador y con esa puede ver netflix en la pc y e puede activar la tv por medio de codigo, espero que sea de gran ultilidad.


by @hacker056
