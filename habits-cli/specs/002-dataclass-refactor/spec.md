# Spec 002 — Refactorización del modelo de dominio a Dataclasses

## Contexto y objetivo
Actualmente, el núcleo de la aplicación (`habits/core.py`) representa las entidades principales mediante diccionarios genéricos de Python (`dict[str, Any]`). Aunque esto fue adecuado para el MVP, carece de seguridad de tipos en tiempo de desarrollo y distribuye la lógica del dominio en funciones libres.

Esta especificación define la refactorización interna para introducir un nuevo módulo independiente `habits/types.py` con `dataclasses` tipadas de la biblioteca estándar de Python (`Habit`, `HabitStore`, `HabitSummary`) y trasladar la lógica de negocio a métodos de estas clases. La conversión entre el formato de persistencia y las dataclasses se gestionará mediante funciones en `storage.py` para mantener las clases del dominio totalmente desacopladas de la infraestructura, conservando el 100% de compatibilidad con el comportamiento externo de la CLI.

## Usuarios / actores
Desarrolladores y mantenedores del proyecto `habits-cli`. No hay impacto directo en los usuarios finales de la herramienta de línea de comandos.

## Historias de usuario
- H1: Como mantenedor del código quiero disponer de un módulo independiente `habits/types.py` con `dataclasses` fuertemente tipadas para contar con autocompletado, validación de tipos y un modelo de dominio centralizado sin dependencias circulares.
- H2: Como mantenedor del código quiero encapsular el comportamiento del dominio (como calcular la racha o marcar un hábito como completado) en métodos de las `dataclasses` para mejorar la cohesión y mantenibilidad.
- H3: Como mantenedor del código quiero que la lógica de conversión y almacenamiento resida en `storage.py` para que las dataclasses no conozcan el origen o formato de sus datos.

## Requisitos funcionales (criterios de aceptación en EARS)

### Arquitectura de tipos (Módulo `habits/types.py`)
- RF-1: EL SISTEMA definirá un nuevo módulo `habits/types.py` sin dependencias de otros módulos del proyecto (`habits/core.py`, `habits/storage.py`, `habits/cli.py`), del cual importarán los demás módulos.
- RF-2: EL SISTEMA definirá en `types.py` la dataclass `Habit` para representar un hábito (con campos para nombre, fecha de creación e historial de fechas completadas).
- RF-3: EL SISTEMA definirá en `types.py` la dataclass `HabitStore` contenedora de la versión del esquema y la lista de objetos `Habit`.
- RF-4: EL SISTEMA definirá en `types.py` la dataclass `HabitSummary` para las filas proyectadas al listar hábitos (nombre y racha).

### Encapsulamiento de lógica en métodos
- RF-5: MIENTRAS se opere sobre un objeto `Habit`, EL SISTEMA calculará la racha de días consecutivos mediante un método `streak(today: date) -> int` perteneciente a dicha clase, preservando las reglas del RF-10 de la Spec 001.
- RF-6: CUANDO se marque un hábito como completado (`mark_done(today: date)`), EL SISTEMA ejecutará el marcado a través de un método de la dataclass (`Habit` o `HabitStore`), garantizando la idempotencia y retornando si ya estaba marcado.
- RF-7: CUANDO se añada un hábito a la colección (`add_habit(name: str, today: date)`), EL SISTEMA ejecutará la validación de nombre no vacío y la verificación de duplicados (insensible a mayúsculas/espacios) mediante un método de `HabitStore`.
- RF-8: CUANDO se solicite listar hábitos (`list_habits(today: date)`), EL SISTEMA devolverá una lista de objetos `HabitSummary` ordenados por racha descendente y por nombre alfabético.

### Conversión y Serialización en Persistencia
- RF-9: EL SISTEMA implementará las funciones de conversión desde y hacia estructuras dict/JSON internamente dentro de `storage.py`, manteniendo a las dataclasses de `types.py` agnósticas de la persistencia.
- RF-10: SI el archivo de almacenamiento no puede ser deserializado a la estructura `HabitStore` esperada, ENTONCES EL SISTEMA mantendrá el lanzamiento de `StorageError` sin modificar el archivo local (cumpliendo RF-11 de Spec 001).

### Integración y compatibilidad
- RF-11: EL SISTEMA mantendrá exactamente la misma interfaz pública de terminal (`habits add`, `habits done`, `habits list`), códigos de salida (0 y 1) y mensajes al usuario definidos en la Spec 001.

## Requisitos no funcionales
- Emplear exclusivamente el módulo `dataclasses` de la biblioteca estándar de Python (compatibilidad con Python 3.12+).
- Mantener tipado estricto (type hints) en todas las clases, atributos y métodos públicos.
- Respuesta inmediata en ejecución (<1 s).

## Casos límite
- Estructura JSON válida pero con tipos inconsistentes en los campos → manejado como `StorageError` en `storage.py`.
- Hábito sin fechas completadas → `streak(today)` debe retornar 0.
- Comparación de nombres con espacios o mayúsculas → encapsulada en la lógica de normalización de la dataclass.

## Fuera de alcance
- Alterar el formato del archivo `habits.json` en disco.
- Agregar bibliotecas externas como `pydantic`, `attrs` o `marshmallow`.
- Modificar los comandos CLI o agregar nuevas funcionalidades visibles para el usuario final.

## Criterios de finalización
- Creación del nuevo módulo `habits/types.py` conteniendo `Habit`, `HabitStore` y `HabitSummary`.
- Sustitución total de `dict[str, Any]` por las dataclasses importadas desde `types.py` en `core.py`, `storage.py` y `cli.py`.
- Funciones de conversión integradas en `storage.py`.
- Suite de tests unitarios e integración en verde al ejecutar `pytest -q`.

## Dudas abiertas
- Ninguna.
