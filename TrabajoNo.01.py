import pandas as pd
import random

class Item:
    def __init__(self, id, valor, peso):
        self.id = id
        self.valor = valor
        self.peso = peso

def cargar_desde_archivo(ruta):
    try:
        df = pd.read_csv(ruta) # Espera columnas: id, valor, peso
        return [Item(row['id'], row['valor'], row['peso']) for _, row in df.iterrows()]
    except Exception as e:
        print(f"Error cargando archivo: {e}")
        return []

# --- HEURÍSTICAS DE SENSIBILIDAD (INDICADORES) ---
def sensibilidad(item, tipo, k1=1, k2=1):
    if tipo == '1': return item.valor / item.peso if item.peso > 0 else 0 # Densidad
    if tipo == '2': return item.valor # Mayor Valor
    if tipo == '3': return 1 / item.peso if item.peso > 0 else 0 # Menor Peso
    if tipo == '4': return (k1 * item.valor) + (k2 * (1/item.peso)) # Combinación Lineal
    return 0

# --- ALGORITMOS DE CONSTRUCCIÓN ---
def greedy_knapsack(items, capacidad, tipo_sens, k1=1, k2=1, semilla=None):
    if semilla is not None:
        random.seed(semilla)
        random.shuffle(items) # Para heurística al azar
     
    # Ordenar según indicador
    items_ordenados = sorted(items, key=lambda x: sensibilidad(x, tipo_sens, k1, k2), reverse=True)
    
    mochila = []
    peso_total = 0
    valor_total = 0
    vector_binario = [0] * len(items)

    for item in items_ordenados:
        if peso_total + item.peso <= capacidad:
            mochila.append(item)
            peso_total += item.peso
            valor_total += item.valor
            vector_binario[items.index(item)] = 1
            
    return vector_binario, valor_total, peso_total

# --- ALGORITMO DE REDUCCIÓN ---
def reduction_knapsack(items, capacidad, tipo_sens, k1=1, k2=1):
    items_copia = sorted(items, key=lambda x: sensibilidad(x, tipo_sens, k1, k2), reverse=True)
    
    peso_actual = sum(it.peso for it in items_copia)
    
    #Bucle destructor 
    while peso_actual > capacidad and items_copia:
        item_eliminado = items_copia.pop() # Sacamos el peor (el último)
        peso_actual -= item_eliminado.peso # Actualizamos el peso
        
    # Construccion del vector
    vector_binario = [0] * len(items)
    valor_total = 0
    
    for item in items_copia:
        valor_total += item.valor
        vector_binario[items.index(item)] = 1 
        
    return vector_binario, valor_total, peso_actual

# --- ALGORITMO DE ALTERNANCIA ---
def alternating_knapsack(items, capacidad, orden):
    # orden: lista de tipos de sensibilidad, ej ['1','2','3']
    mochila_actual = []
    peso_actual = 0
    valor_actual = 0
    vector_binario = [0] * len(items)
    for tipo in orden:
        items_restantes = [it for it in items if it not in mochila_actual]
        if not items_restantes:
            break
        items_ordenados = sorted(items_restantes, key=lambda x: sensibilidad(x, tipo), reverse=True)
        for item in items_ordenados:
            if peso_actual + item.peso <= capacidad:
                mochila_actual.append(item)
                peso_actual += item.peso
                valor_actual += item.valor
                vector_binario[items.index(item)] = 1
    return vector_binario, valor_actual, peso_actual

# --- LÓGICA PRINCIPAL ---
def menu():
    print("--- SOLUCIONADOR MOCHILA BINARIA ---")
    ruta = input("Ingrese ruta del archivo (csv): ")
    items = cargar_desde_archivo(ruta)
    if not items:
        print("No se pudieron cargar ítems. Saliendo.")
        return

    while True:
        try:
            capacidad_max = float(input("Capacidad de la mochila: "))
            if capacidad_max < 0:
                print("Error: la capacidad no puede ser negativa. Intente nuevamente.")
                continue
            break
        except ValueError:
            print("Error: capacidad inválida. Ingrese un número válido.")

    print("\nElija tipo de Metaheurística:\n1. Constructiva\n2. Reducción\n3. Descomposición")
    while True:
        opcion_meta = input("Selección: ").strip()
        if opcion_meta in {'1', '2', '3'}:
            break
        print("Error: debe seleccionar una opción válida entre 1 y 3.")

    resultados = []

    if opcion_meta == '1': # Constructivas
        print("\nHeurísticas de Sensibilidad:\n1. Valor/Peso\n2. Máximo Valor\n3. Mínimo Peso\n4. Comb. Lineal\n5. Azar\n6. Alternancia")
        selecciones = [s.strip() for s in input("Elija las heurísticas separadas por coma (ej: 1,2,4): ").split(',') if s.strip()]
        if len(selecciones) > 3:
            print("Error: no puede ingresar más de 3 heurísticas de sensibilidad.")
            return
        
        for s in selecciones:
            if s == '4':
                n_comb = int(input("¿Cuántas combinaciones K1, K2 desea? "))
                for _ in range(n_comb):
                    k1 = float(input("K1: "))
                    k2 = float(input("K2: "))
                    res = greedy_knapsack(items, capacidad_max, '4', k1, k2)
                    resultados.append((f"Comb. Lineal ({k1},{k2})", *res))
            elif s == '5':
                semilla = int(input("Ingrese semilla: "))
                res = greedy_knapsack(items, capacidad_max, '1', semilla=semilla)
                resultados.append(("Azar", *res))
            elif s == '6':
                orden = [o.strip() for o in input("Elija hasta 3 heurísticas para alternar (ej: 1,2,3): ").split(',') if o.strip()]
                if len(orden) > 3:
                    print("Error: no puede ingresar más de 3 heurísticas para alternancia.")
                    return
                res = alternating_knapsack(items, capacidad_max, orden)
                resultados.append(("Alternancia " + ','.join(orden), *res))
            else:
                res = greedy_knapsack(items, capacidad_max, s)
                resultados.append((f"Sensibilidad {s}", *res))

    elif opcion_meta == '2': # Reducción
        print("\nHeurísticas de Sensibilidad para Reducción:\n1. Valor/Peso\n2. Máximo Valor\n3. Mínimo Peso\n4. Comb. Lineal")
        selecciones = [s.strip() for s in input("Elija las heurísticas separadas por coma (ej: 1,2,4): ").split(',') if s.strip()]
        if len(selecciones) > 3:
            print("Error: no puede ingresar más de 3 heurísticas de sensibilidad.")
            return
        
        for s in selecciones:
            if s == '4':
                n_comb = int(input("¿Cuántas combinaciones K1, K2 desea? "))
                for _ in range(n_comb):
                    k1 = float(input("K1: "))
                    k2 = float(input("K2: "))
                    res = reduction_knapsack(items, capacidad_max, '4', k1, k2)
                    resultados.append((f"Reducción Comb. Lineal ({k1},{k2})", *res))
            else:
                res = reduction_knapsack(items, capacidad_max, s)
                resultados.append((f"Reducción Sensibilidad {s}", *res))

    elif opcion_meta == '3': # Descomposición
        while True:
            try:
                n_partes = int(input("¿En cuántas submochilas dividir? "))
                if n_partes <= 0:
                    print("Debe ingresar al menos 1 submochila.")
                    continue
                break
            except ValueError:
                print("Error: debe ingresar un número entero válido.")


        capacidad_subs = []
        while True:
            capacidad_subs = []
            for i in range(n_partes):
                while True:
                    try:
                        cap_sub = float(input(f"Capacidad submochila {i+1}: "))
                        if cap_sub < 0:
                            print("La capacidad no puede ser negativa. Intente nuevamente.")
                            continue
                        capacidad_subs.append(cap_sub)
                        break
                    except ValueError:
                        print("Error: capacidad inválida. Ingrese un número válido.")

            suma_subs = sum(capacidad_subs)
            if abs(suma_subs - capacidad_max) > 1e-9:
                print(f"Error: las capacidades deben sumar {capacidad_max}. Actualmente suman {suma_subs}.")
                print("Ingrese nuevamente las capacidades de las submochilas.")
                continue
            break

        items_restantes = items.copy()
        vector_global = [0] * len(items)
        valor_global = 0
        peso_global = 0
        heuristicas_utilizadas = set()
        
        for i in range(n_partes):
            while True:
                sens_sub = input(f"Heurística para submochila {i+1} (1-5): ").strip()
                if sens_sub not in {'1', '2', '3', '4', '5'}:
                    print("Error: la heurística debe ser un número entre 1 y 5.")
                    continue
                if sens_sub in heuristicas_utilizadas:
                    print("Error: esa heurística ya fue usada en otra submochila. Elija otra.")
                    continue
                heuristicas_utilizadas.add(sens_sub)
                break

            cap_sub = capacidad_subs[i]
            if sens_sub == '4':
                while True:
                    try:
                        k1 = float(input("K1: "))
                        break
                    except ValueError:
                        print("Error: K1 debe ser un número válido.")
                while True:
                    try:
                        k2 = float(input("K2: "))
                        break
                    except ValueError:
                        print("Error: K2 debe ser un número válido.")
                v_bin, v_val, v_p = greedy_knapsack(items_restantes, cap_sub, '4', k1, k2)
            elif sens_sub == '5':
                while True:
                    try:
                        semilla = int(input("Semilla: "))
                        break
                    except ValueError:
                        print("Error: la semilla debe ser un número entero válido.")
                v_bin, v_val, v_p = greedy_knapsack(items_restantes, cap_sub, '1', semilla=semilla)
            else:
                v_bin, v_val, v_p = greedy_knapsack(items_restantes, cap_sub, sens_sub)
            
            # Actualizar global
            valor_global += v_val
            peso_global += v_p
            items_seleccionados = [items_restantes[i] for i, val in enumerate(v_bin) if val == 1]

            for item in items_seleccionados:
                vector_global[items.index(item)] = 1
                items_restantes.remove(item)
        resultados.append(("Descomposición", vector_global, valor_global, peso_global))

    # MOSTRAR RESULTADOS
    print("\n--- RESULTADOS ---")
    mejor = max(resultados, key=lambda x: x[2])
    for r in resultados:
        print(f"\nMétodo: {r[0]}")
        print(f"Vector: {r[1]}")
        print(f"Valor: {r[2]} | Peso: {r[3]}")
    
    print(f"\nLA MEJOR SOLUCIÓN ES: {mejor[0]} con Valor: {mejor[2]}")

menu()