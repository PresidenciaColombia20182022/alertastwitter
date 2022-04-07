# alertastwitter
Repositorio del código que permite alertar via Telegram las tendencias de gobierno al día de hoy.

El código alertas.py descarga las tendencias del día utilizando la librería Tweepy. Seguido a esto, de cada tendencia descarga 50 tweets y los clasifica mediante machine learning como tweet de 'Política' u 'Otro'.

Si el número de tweets clasificados como 'Política' cubren el 70% o más de los tweets descargados, entonces la tendencia es relacionada a gobierno.

Las tendencias que son clasificadas como 'Política' se envían vía Telegram junto con su volumen de menciones y la fecha del día en que se obtiene este dato. Es posible igualmente guardar las tendencias en una base de datos relacional o tipo SQL como PosgresQL.

La carpeta /models tiene el modelo de Machine Learning que fue entrenado mediante Regresión Logística para determinar si un tweet tenía relación o no con el tema de 'Política'.

La carpeta /envalertas contiene el ambiente con el que se instalaron las diferentes librerías necesarias para correr el proyecto.
