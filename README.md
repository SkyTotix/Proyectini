# 📚 Sistema POS - Librería Callejera

Sistema de Punto de Venta diseñado específicamente para vendedores de libros en comercio informal callejero.

## 🚀 Inicio Rápido

```bash
# Clonar el repositorio
git clone https://github.com/SkyTotix/Proyectini.git
cd Proyectini

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python run.py
```

O directamente:
```bash
streamlit run src/app.py
```

## 🎯 Características Principales

- ✅ **Base de datos local** - SQLite (no requiere servidor)
- ✅ **Interfaz web moderna** - Streamlit
- ✅ **Gestión completa de inventario** - Libros, stock, precios
- ✅ **Sistema de ventas intuitivo** - Carrito de compras
- ✅ **Reportes y estadísticas** - Análisis de ventas
- ✅ **Instalación sencilla** - Un solo comando

## 📁 Estructura del Proyecto

```
proyectito/
├── src/                    # Código fuente principal
│   ├── app.py             # Aplicación principal
│   ├── config.py          # Configuraciones
│   └── models/            # Modelos de datos
├── database/              # Gestión de base de datos
├── ui/                    # Interfaz de usuario
│   ├── pages/             # Páginas de Streamlit
│   └── components/        # Componentes reutilizables
├── utils/                 # Utilidades
├── data/                  # Base de datos SQLite
├── tests/                 # Pruebas
├── docs/                  # Documentación
├── scripts/               # Scripts de automatización
├── requirements.txt       # Dependencias
├── run.py                 # Script de inicio
└── README.md             # Esta documentación
```

## 🚀 Instalación y Uso

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar el sistema

```bash
python run.py
```

O directamente con Streamlit:
```bash
streamlit run src/app.py
```

### 3. Acceder al sistema

El sistema se abrirá automáticamente en tu navegador en:
```
http://localhost:8501
```

## 📋 Estado del Desarrollo

### ✅ Completado
- [x] Estructura de carpetas organizada
- [x] Configuración básica del proyecto
- [x] Script de inicio funcional
- [x] Interfaz principal básica

### 🔄 En Desarrollo
- [ ] Base de datos y modelos
- [ ] Gestión de inventario
- [ ] Sistema de ventas
- [ ] Reportes y dashboard

### 📅 Próximas Etapas
- [ ] Implementar base de datos SQLite
- [ ] Crear modelos de datos
- [ ] Desarrollar interfaz de inventario
- [ ] Sistema de ventas con carrito
- [ ] Dashboard de reportes

## 🛠️ Tecnologías Utilizadas

- **Python 3.7+**
- **Streamlit** - Interfaz web
- **SQLite** - Base de datos local
- **Pandas** - Manipulación de datos
- **Plotly** - Gráficos y visualizaciones

## 📞 Soporte

Este sistema está siendo desarrollado específicamente para el comercio informal de libros en México.

## 📄 Licencia

Desarrollado para uso educativo y comercial informal.
