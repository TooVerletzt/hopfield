# hopfield.py
# Hopfield 8x5 para figuras geométricas

# ---------------- utilidades I/O ----------------
def leer_matriz_txt(ruta):
    # Lee archivo 8x5 con 0/1 y devuelve matriz de enteros
    M = []
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea == "":
                continue
            fila = []
            token = ""
            i = 0
            while i < len(linea):
                c = linea[i]
                if c.isspace():
                    if token != "":
                        fila.append(int(token))
                        token = ""
                else:
                    token += c
                i += 1
            if token != "":
                fila.append(int(token))
            if len(fila) > 0:
                M.append(fila)
    return M  # lista de listas

def aplanar(M):  # 8x5 -> vector 40
    v = []
    i = 0
    while i < len(M):
        j = 0
        while j < len(M[0]):
            v.append(M[i][j])
            j += 1
        i += 1
    return v

def bin_a_pm1(v):  # 0 -> -1, 1 -> 1
    i = 0
    while i < len(v):
        if v[i] == 0:
            v[i] = -1
        else:
            v[i] = 1
        i += 1
    return v

def imprimir_grid(v, R, C, titulo):
    print("\n" + titulo)
    r = 0; k = 0
    while r < R:
        fila = ""
        c = 0
        while c < C:
            fila += "█" if v[k] == 1 else "·"
            c += 1; k += 1
        print(fila)
        r += 1

def imprimir_vector(v, titulo):
    # Solo para ver el producto U·T
    s = " ".join(str(x) for x in v)
    print(f"{titulo}: {s}")

# operaciones
def producto_externo(v):   # N x N con 2 for (v[i]*v[j])
    n = len(v)
    M = []
    i = 0
    while i < n:
        fila = []
        j = 0
        while j < n:
            fila.append(v[i] * v[j])
            j += 1
        M.append(fila)
        i += 1
    return M

def sumar_matrices(A, B):
    n = len(A)
    C = []
    i = 0
    while i < n:
        fila = []
        j = 0
        while j < n:
            fila.append(A[i][j] + B[i][j])
            j += 1
        C.append(fila)
        i += 1
    return C

def diagonal_cero(M):
    i = 0
    while i < len(M):
        M[i][i] = 0
        i += 1
    return M

def vector_por_matriz(u, T):
    n = len(u)
    y = []
    j = 0
    while j < n:
        s = 0
        i = 0
        while i < n:
            s += u[i] * T[i][j]
            i += 1
        y.append(s)
        j += 1
    return y

def escalon(x, prev):
    if x > 0:   return 1
    elif x < 0: return -1
    else:       return prev  # si es 0, conserva el valor previo

def iguales(a, b):
    i = 0
    while i < len(a):
        if a[i] != b[i]: return False
        i += 1
    return True

# entrenamiento
def entrenar(patrones):
    # Suma de productos externos y diagonal=0
    n = len(patrones[0])
    # S = 0
    S = []
    i = 0
    while i < n:
        fila = []
        j = 0
        while j < n:
            fila.append(0)
            j += 1
        S.append(fila)
        i += 1

    # acumular X^T·X de cada patrón
    p = 0
    while p < len(patrones):
        OP = producto_externo(patrones[p])
        S = sumar_matrices(S, OP)
        p += 1

    # T = S con diagonal en 0
    T = []
    i = 0
    while i < n:
        fila = []
        j = 0
        while j < n:
            fila.append(S[i][j])
            j += 1
        T.append(fila)
        i += 1
    diagonal_cero(T)
    return T

def recuperar(u0, T, R, C, max_iter=50, verbose=True):
    # Recuperación sincrónica estilo do-while
    U = u0[:]
    k = 0
    if verbose:
        imprimir_grid(U, R, C, f"U({k})  (entrada)")

    while True:
        y = vector_por_matriz(U, T)
        if verbose:
            imprimir_vector(y, f"U({k})·T")

        # aplicar función de activación
        U_next = []
        j = 0
        while j < len(U):
            U_next.append(escalon(y[j], U[j]))
            j += 1

        k += 1
        if verbose:
            imprimir_grid(U_next, R, C, f"U({k})")

        if iguales(U_next, U):
            if verbose:
                print("\nEstable, No cambió entre iteraciones.")
            return U_next

        if k >= max_iter:
            if verbose:
                print("\nTope de iteraciones alcanzado (posible ciclo).")
            return U_next

        U = U_next  # siguiente vuelta

# main
def main():
    R, C = 8, 5  # 8x5 => N=40

    # Usar nombres relativos
    archivos = [
        "dataset/trianguloRec.txt",
        "dataset/rectangulo.txt",
        "dataset/hexagono.txt",
        "dataset/rombo.txt",
        "dataset/trianguloInvertido.txt",
        "dataset/cuña.txt",
    ]

    # archivo de prueba
    archivo_prueba = "dataset/prueba.txt"

    print("Cargando patrones:")
    for ruta in archivos:
        print(" -", ruta)

    # 2) Cargar, aplanar y convertir a ±1
    patrones = []
    idx = 0
    while idx < len(archivos):
        M = leer_matriz_txt(archivos[idx])

        # validación simple 8x5
        if len(M) != R or len(M[0]) != C:
            print("Formato inválido en", archivos[idx], "(se esperaba 8x5)")
            return

        v = aplanar(M)
        bin_a_pm1(v)
        patrones.append(v)
        idx += 1

    # 3) Entrenar
    T = entrenar(patrones)
    print("\nEntrenamiento listo. (T es 40x40)")

    # 4) Cargar patrón de prueba (desconocido/ruidoso)
    print("\nArchivo de prueba:", archivo_prueba)
    M_test = leer_matriz_txt(archivo_prueba)
    if len(M_test) != R or len(M_test[0]) != C:
        print("Formato inválido en archivo de prueba (se esperaba 8x5)")
        return
    A = aplanar(M_test)
    bin_a_pm1(A)

    imprimir_grid(A, R, C, "Entrada (A)")

    # 5) Recuperar (mostrando TODAS las iteraciones)
    U = recuperar(A, T, R, C, max_iter=50, verbose=True)

    # Resultado final
    imprimir_grid(U, R, C, "Salida(U)")

if __name__ == "__main__":
    main()
