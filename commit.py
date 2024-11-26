import os

# Ruta al programa ejecutable (por ejemplo, /bin/ls en sistemas Unix)
programa = "/bin/ls"

# Argumentos para el programa (el primero suele ser el nombre del programa)
args = {["git", "add", "."], ["git", "commit", "-m", sys.argv[1]], ["git", "push"]}

# Variables de entorno (puedes copiar las existentes con os.environ)
entorno = os.environ.copy()

# Ejecutar el programa
for x < 3:
	os.execve(args, args, entorno)
