import os
import sys
#test
# Ruta al programa ejecutable (por ejemplo, /bin/ls en sistemas Unix)
programa = "/usr/bin/git"

# Argumentos para el programa (el primero suele ser el nombre del programa)
args = [["git", "add", "."], ["git", "commit", "-m", sys.argv[1]], ["git", "push"]]

# Variables de entorno (puedes copiar las existentes con os.environ)
entorno = os.environ.copy()

# Ejecutar el programa
for i in range(3):
	pid = os.fork()
	if pid == 0:
		os.execve(programa, args[i], entorno)
	os.wait()
