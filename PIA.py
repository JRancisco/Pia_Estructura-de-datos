import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

conn = sqlite3.connect('renta_bicicletas.db')
cursor = conn.cursor()

def crear_tablas():
    cursor.execute('''CREATE TABLE IF NOT EXISTS Unidad (
                        clave INTEGER PRIMARY KEY AUTOINCREMENT,
                        rodada INTEGER CHECK(rodada IN (20, 26, 29)),
                        color TEXT NOT NULL CHECK(LENGTH(color) <= 15)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Cliente (
                        clave INTEGER PRIMARY KEY AUTOINCREMENT,
                        apellidos TEXT NOT NULL CHECK(LENGTH(apellidos) <= 40),
                        nombres TEXT NOT NULL CHECK(LENGTH(nombres) <= 40),
                        telefono TEXT NOT NULL CHECK(LENGTH(telefono) = 10)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Prestamo (
                        folio INTEGER PRIMARY KEY AUTOINCREMENT,
                        clave_unidad INTEGER NOT NULL,
                        clave_cliente INTEGER NOT NULL,
                        fecha_prestamo TEXT NOT NULL,
                        dias_prestamo INTEGER NOT NULL CHECK(dias_prestamo BETWEEN 1 AND 14),
                        fecha_retorno TEXT,
                        FOREIGN KEY(clave_unidad) REFERENCES Unidad(clave),
                        FOREIGN KEY(clave_cliente) REFERENCES Cliente(clave)
                    )''')
    conn.commit()

def submenu_listado_unidades():
    mostrar_ruta(["Menú Principal", "Listado de Unidades"])
    while True:
        print("\nListado de Unidades >")
        print("1. Listado Completo")
        print("2. Filtrar por Rodada")
        print("3. Filtrar por Color")
        print("4. Volver")
        opcion = input("Seleccione: ")

        if opcion == "1":
            unidades = pd.read_sql("SELECT * FROM Unidad", conn)
            if unidades.empty:
                print("No hay unidades registradas.")
            else:
                print(unidades)

        elif opcion == "2":
            rodada = solicitar_entero("Ingrese la rodada (20, 26, 29): ", 20, 29)
            unidades = pd.read_sql(f"SELECT * FROM Unidad WHERE rodada = {rodada}", conn)
            if unidades.empty:
                print(f"No hay unidades con rodada {rodada}.")
            else:
                print(unidades)

        elif opcion == "3":
            color = solicitar_texto("Ingrese el color: ", 15)
            unidades = pd.read_sql(f"SELECT * FROM Unidad WHERE color LIKE ?", conn, params=(f"%{color}%",))
            if unidades.empty:
                print(f"No hay unidades con color '{color}'.")
            else:
                print(unidades)

        elif opcion == "4":
            break  

        else:
            print("Opción no válida. Intente de nuevo.")

def submenu_reportes():
    mostrar_ruta(["Menú Principal", "Informes", "Reportes"])
    while True:
        print("1. Clientes")
        print("2. Retrasos")
        print("3. Préstamos por retornar")
        print("4. Listado de unidades")
        print("5. Préstamos por período")
        print("6. Volver")
        opcion = input("Seleccione: ")

        if opcion == "1":
            submenu_clientes_reportes()  
        elif opcion == "2":
            retrasos = pd.read_sql(
                "SELECT * FROM Prestamo WHERE fecha_retorno IS NULL "
                "AND julianday('now') - julianday(fecha_prestamo) > dias_prestamo", conn
            )
            print(retrasos)
            exportar_reporte(retrasos, "retrasos")
        elif opcion == "3":
            retornar = pd.read_sql("SELECT * FROM Prestamo WHERE fecha_retorno IS NULL", conn)
            print(retornar)
            exportar_reporte(retornar, "prestamos_por_retornar")
        elif opcion == "4":
            mostrar_unidades()
        elif opcion == "5":
            prestamos_por_periodo()
        elif opcion == "6":
            break
        else:
            print("Opción no válida. Intente de nuevo.")

def submenu_analisis():
    mostrar_ruta(["Menú Principal", "Análisis"])
    while True:
        print("1. Duración de préstamos")
        print("2. Ranking de clientes")
        print("3. Preferencias de rentas")
        print("4. Volver")
        opcion = input("Seleccione: ")
        if opcion == "1":
            prestamos = pd.read_sql("SELECT dias_prestamo FROM Prestamo", conn)
            print(prestamos.describe())
        elif opcion == "2":
            ranking = pd.read_sql(
                "SELECT c.clave, c.nombres || ' ' || c.apellidos AS nombre, c.telefono, COUNT(*) as total "
                "FROM Cliente c JOIN Prestamo p ON c.clave = p.clave_cliente "
                "GROUP BY c.clave ORDER BY total DESC", conn
            )
            print(ranking)
        elif opcion == "3":
            submenu_preferencias()
        elif opcion == "4":
            break

def submenu_informes():
    mostrar_ruta(["Menú Principal", "Informes"])
    while True:
        print("1. Reportes")
        print("2. Análisis")
        print("3. Volver")
        opcion = input("Seleccione: ")
        if opcion == "1":
            submenu_reportes()
        elif opcion == "2":
            submenu_analisis()
        elif opcion == "3":
            break

def submenu_reportes():
    while True:
        mostrar_ruta(["Menú Principal", "Informes", "Reportes"])
        print("1. Clientes")
        print("2. Retrasos")
        print("3. Préstamos por retornar")
        print("4. Listado de unidades")
        print("5. Préstamos por período")
        print("6. Volver")
        opcion = input("Seleccione: ")

        if opcion == "1":
            submenu_clientes_reportes()  
        elif opcion == "2":
            retrasos = pd.read_sql(
                "SELECT * FROM Prestamo WHERE fecha_retorno IS NULL "
                "AND julianday('now') - julianday(fecha_prestamo) > dias_prestamo", conn
            )
            print(retrasos)
            exportar_reporte(retrasos, "retrasos")
        elif opcion == "3":
            retornar = pd.read_sql("SELECT * FROM Prestamo WHERE fecha_retorno IS NULL", conn)
            print(retornar)
            exportar_reporte(retornar, "prestamos_por_retornar")
        elif opcion == "4":
            mostrar_unidades()
        elif opcion == "5":
            prestamos_por_periodo()
        elif opcion == "6":
            break
        else:
            print("Opción no válida. Intente de nuevo.")

def reporte_cliente_especifico():
    mostrar_clientes() 
    clave_cliente = solicitar_entero("Ingrese la clave del cliente: ")
    prestamos_cliente = pd.read_sql(
        "SELECT p.folio, u.rodada, u.color, p.fecha_prestamo, p.dias_prestamo, p.fecha_retorno "
        "FROM Prestamo p "
        "JOIN Unidad u ON p.clave_unidad = u.clave "
        "WHERE p.clave_cliente = ?", conn, params=(clave_cliente,)
    )
    
    if prestamos_cliente.empty:
        print("No se encontraron préstamos para el cliente seleccionado.")
    else:
        print(prestamos_cliente)
        exportar_reporte(prestamos_cliente, f"reporte_cliente_{clave_cliente}")

def prestamos_por_periodo():
    fecha_inicio = input("Ingrese la fecha de inicio (AAAA-MM-DD): ")
    fecha_fin = input("Ingrese la fecha de fin (AAAA-MM-DD): ")
    
    prestamos_periodo = pd.read_sql(
        "SELECT p.folio, u.rodada, u.color, p.fecha_prestamo, p.dias_prestamo, p.fecha_retorno, "
        "c.nombres || ' ' || c.apellidos AS cliente "
        "FROM Prestamo p "
        "JOIN Unidad u ON p.clave_unidad = u.clave "
        "JOIN Cliente c ON p.clave_cliente = c.clave "
        "WHERE p.fecha_prestamo BETWEEN ? AND ?", conn, params=(fecha_inicio, fecha_fin)
    )
    
    if prestamos_periodo.empty:
        print("No se encontraron préstamos en el período seleccionado.")
    else:
        print(prestamos_periodo)
        exportar_reporte(prestamos_periodo, f"prestamos_{fecha_inicio}_a_{fecha_fin}")

def submenu_registros():
    mostrar_ruta(["Menú Principal", "Registros"])
    while True:
        print("1. Registrar Unidad")
        print("2. Registrar Cliente")
        print("3. Volver")
        opcion = input("Seleccione: ")
        if opcion == "1":
            registrar_unidad()
        elif opcion == "2":
            registrar_cliente()
        elif opcion == "3":
            break
        else:
            print("Opción no válida. Intente de nuevo.")

def registrar_unidad():
    rodada = solicitar_entero("Ingrese la rodada (20, 26, 29): ", 20, 29)
    color = solicitar_texto("Ingrese el color de la unidad (máximo 15 caracteres): ", 15)
    cursor.execute("INSERT INTO Unidad (rodada, color) VALUES (?, ?)", (rodada, color))
    conn.commit()
    print("Unidad registrada correctamente.")

def registrar_cliente():
    apellidos = solicitar_texto("Ingrese los apellidos del cliente (máximo 40 caracteres): ", 40)
    nombres = solicitar_texto("Ingrese los nombres del cliente (máximo 40 caracteres): ", 40)
    telefono = solicitar_telefono()
    cursor.execute("INSERT INTO Cliente (apellidos, nombres, telefono) VALUES (?, ?, ?)", 
                   (apellidos, nombres, telefono))
    conn.commit()
    print("Cliente registrado correctamente.")

def registrar_prestamo():
    unidades = pd.read_sql(
        "SELECT * FROM Unidad WHERE clave NOT IN (SELECT clave_unidad FROM Prestamo WHERE fecha_retorno IS NULL)", conn
    )
    if unidades.empty:
        print("No hay unidades disponibles para prestar.")
        return
    print(unidades[['clave', 'rodada', 'color']])

    clientes = pd.read_sql("SELECT * FROM Cliente", conn)
    print(clientes[['clave', 'apellidos', 'nombres']])

    clave_unidad = solicitar_entero("Ingrese la clave de la unidad: ")
    clave_cliente = solicitar_entero("Ingrese la clave del cliente: ")
    dias_prestamo = solicitar_entero("Ingrese la cantidad de días (1-14): ", 1, 14)

    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    fecha_prestamo = input(f"Ingrese la fecha (AAAA-MM-DD) o Enter para usar {fecha_actual}: ") or fecha_actual

    cursor.execute(
        "INSERT INTO Prestamo (clave_unidad, clave_cliente, fecha_prestamo, dias_prestamo) VALUES (?, ?, ?, ?)",
        (clave_unidad, clave_cliente, fecha_prestamo, dias_prestamo)
    )
    conn.commit()
    print("Préstamo registrado correctamente.")

def registrar_retorno():
    prestamos = pd.read_sql("SELECT * FROM Prestamo WHERE fecha_retorno IS NULL", conn)
    if prestamos.empty:
        print("No hay préstamos pendientes.")
        return
    print(prestamos[['folio', 'clave_unidad', 'fecha_prestamo']])

    folio = solicitar_entero("Ingrese el folio del préstamo: ")
    fecha_retorno = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("UPDATE Prestamo SET fecha_retorno = ? WHERE folio = ?", (fecha_retorno, folio))
    conn.commit()
    print("Retorno registrado correctamente.")


def menu_principal():
    while True:
        print("\nMENÚ PRINCIPAL")
        print("1. Registros")
        print("2. Registrar Préstamo")
        print("3. Registrar Retorno")
        print("4. Informes")
        print("5. Salir")
        opcion = input("Seleccione: ")

        if opcion == '1':
            submenu_registros() 
        elif opcion == '2':
            registrar_prestamo()
        elif opcion == '3':
            registrar_retorno()
        elif opcion == '4':
            submenu_informes()
        elif opcion == '5':
            if confirmar_salida():
                conn.close()
                print("Saliendo del sistema.")
                break
            else:
                print("Regresando al menú principal...")
        else:
            print("Opción no válida. Intente de nuevo.")

def solicitar_entero(mensaje, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(mensaje))
            if (minimo is not None and valor < minimo) or (maximo is not None and valor > maximo):
                print(f"El valor debe estar entre {minimo} y {maximo}.")
            else:
                return valor
        except ValueError:
            print("Entrada inválida. Debe ingresar un número entero.")

def solicitar_texto(mensaje, longitud_max):
    while True:
        texto = input(mensaje)
        if len(texto) > longitud_max:
            print(f"El texto no debe superar los {longitud_max} caracteres.")
        else:
            return texto

def solicitar_telefono():
    while True:
        telefono = input("Ingrese el teléfono (10 dígitos): ")
        if telefono.isdigit() and len(telefono) == 10:
            return telefono
        else:
            print("Teléfono inválido. Debe contener exactamente 10 dígitos.")
            
def confirmar_salida():
    while True:
        confirmacion = input("¿Está seguro de que desea salir? (S/N): ").strip().lower()
        if confirmacion in ["s", "n"]:
            return confirmacion == "s"
        else:
            print("Opción no válida. Ingrese 'S' para sí o 'N' para no.")

def mostrar_ruta(ruta):
    print(f"\n{' > '.join(ruta)}")

def exportar_reporte(df, nombre):
    formato = input("¿En qué formato desea exportar el reporte? (1: CSV, 2: Excel, 3: Cancelar): ")
    if formato == "1":
        df.to_csv(f"{nombre}.csv", index=False)
        print(f"Reporte exportado como {nombre}.csv")
    elif formato == "2":
        df.to_excel(f"{nombre}.xlsx", index=False)
        print(f"Reporte exportado como {nombre}.xlsx")
    else:
        print("Exportación cancelada.")

def mostrar_clientes():
    clientes = pd.read_sql("SELECT clave, nombres, apellidos FROM Cliente", conn)
    print(clientes)

def mostrar_unidades():
    unidades = pd.read_sql("SELECT clave, color, rodada FROM Unidad", conn)
    print(unidades)

def mostrar_grafica_pastel(data, titulo):
    data.plot(kind='pie', y='total', labels=data.index, autopct='%1.1f%%', legend=False)
    plt.title(titulo)
    plt.ylabel("")
    plt.show()

def mostrar_grafica_barras(data, titulo):
    data.plot(kind='bar', legend=False)
    plt.title(titulo)
    plt.show()

def preferencias_por_rodada():
    data = pd.read_sql("SELECT rodada, COUNT(*) as total FROM Unidad GROUP BY rodada ORDER BY total DESC", conn)
    data.set_index('rodada', inplace=True) 
    print(data)
    mostrar_grafica_pastel(data, "Preferencia por Rodada")

def preferencias_por_color():
    data = pd.read_sql("SELECT color, COUNT(*) as total FROM Unidad GROUP BY color ORDER BY total DESC", conn)
    print(data)
    mostrar_grafica_pastel(data.set_index('color'), "Preferencia por Color")

def preferencias_por_dia():
    data = pd.read_sql(
        "SELECT strftime('%w', fecha_prestamo) as dia, COUNT(*) as total FROM Prestamo GROUP BY dia ORDER BY dia", conn
    )
    print(data)
    mostrar_grafica_barras(data.set_index('dia'), "Preferencia por Día de la Semana")

import re

def solicitar_texto_solo_letras(mensaje, longitud_max):
    while True:
        texto = input(mensaje)
        if not re.match("^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", texto):
            print("Solo se permiten letras y espacios.")
        elif len(texto) > longitud_max:
            print(f"El texto no debe superar los {longitud_max} caracteres.")
        else:
            return texto

def solicitar_telefono():
    while True:
        telefono = input("Ingrese el teléfono (10 dígitos): ")
        if telefono.isdigit() and len(telefono) == 10:
            return telefono
        else:
            print("Teléfono inválido. Debe contener exactamente 10 dígitos.")

def registrar_cliente():
    apellidos = solicitar_texto_solo_letras("Ingrese los apellidos del cliente (máximo 40 caracteres): ", 40)
    nombres = solicitar_texto_solo_letras("Ingrese los nombres del cliente (máximo 40 caracteres): ", 40)
    telefono = solicitar_telefono()
    cursor.execute("INSERT INTO Cliente (apellidos, nombres, telefono) VALUES (?, ?, ?)", 
                   (apellidos, nombres, telefono))
    conn.commit()
    print("Cliente registrado correctamente.")

def registrar_unidad():
    rodada = solicitar_entero("Ingrese la rodada (20, 26, 29): ", 20, 29)
    color = solicitar_texto_solo_letras("Ingrese el color de la unidad (máximo 15 caracteres): ", 15)
    cursor.execute("INSERT INTO Unidad (rodada, color) VALUES (?, ?)", (rodada, color))
    conn.commit()
    print("Unidad registrada correctamente.")

def mostrar_ruta(ruta):
    print(f"\n{' > '.join(ruta)}")

def submenu_clientes_reportes():
    mostrar_ruta(["Menú Principal", "Informes", "Reportes", "Clientes"])
    while True:
        print("1. Listado completo de clientes")
        print("2. Reporte de un cliente específico")
        print("3. Volver")
        opcion = input("Seleccione: ")

        if opcion == "1":
            clientes = pd.read_sql("SELECT * FROM Cliente", conn)
            print(clientes)
            exportar_reporte(clientes, "clientes")
        elif opcion == "2":
            reporte_cliente_especifico()
        elif opcion == "3":
            break
        else:
            print("Opción no válida. Intente de nuevo.")

def submenu_preferencias():
    mostrar_ruta(["Menú Principal", "Análisis", "Preferencias de Rentas"])
    while True:
        print("1. Por rodada")
        print("2. Por color")
        print("3. Por día de la semana")
        print("4. Volver")
        opcion = input("Seleccione: ")
        if opcion == "1":
            preferencias_por_rodada()
        elif opcion == "2":
            preferencias_por_color()
        elif opcion == "3":
            preferencias_por_dia()
        elif opcion == "4":
            break

if __name__ == "__main__":
    crear_tablas()
    menu_principal()