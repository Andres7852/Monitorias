Monitorias App - Paquete

Instrucciones de uso:

1. Crear y activar entorno virtual
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate  # Linux/Mac

2. Instalar dependencias
   pip install -r requirements.txt

3. Inicializar la base de datos (crea instance/monitorias.db and seeds materias)
   python init_db.py

4. Ejecutar la app
   python app.py

Credenciales de prueba:
- Crea cuentas desde /register. Para profesor usa un código válido (ej: PROF2024A).
- Para decano usa DEC2024X.
