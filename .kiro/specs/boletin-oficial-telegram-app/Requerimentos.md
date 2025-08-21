# AppBoletinOficial Argentina v1.0.0


## Objetivo:
Se requiere una aplicación sencilla que analice, en principio, la primera sección del boletin oficial de la republica argentina: "Legislación y Avisos Oficiales" que se publica en  https://otslist.boletinoficial.gob.ar/ots/ . 

## Requerimientos Funcionales
-La aplicacion tiene un calendario donde se elige una fecha (posiblemente la fecha actual)
-El analisis debe explicar la nueva normativa publicada en la sección 1: "Legislación y Avisos Oficiales",  detallando los cambios que introduce con respecto a la normativa anterior.
-Debe contar con una sección de opiniones de expertos sobre los cambios si las hubiera. 
-Cada analisis anterior debe guardarlo en una base de datos para que se pueda recuperar si se introduce 

##Requerimientos No Funcionales
1-Backend : 
a) El backend debe codificarse en Python. Encapsulado en una aws lambda que tiene utiliza un framework LangChase para poder invocar un LLM y asi realizar el analisis.
b) La información se obtiene por pdf buscando, 
   si la fecha es la actual:
    https://s3.arsat.com.ar/cdn-bo-001/pdf-del-dia/primera.pdf
   si la fecha no es la actual el pdf analizar si obtiene de la API seteando la sesion: https://www.boletinoficial.gob.ar/seccion/primera 
b)La base de datos donde se guardan los analisis y opiniones de expertos (por fecha y seccion) es un BD NoSQL-MongoDb que va a ser creada la coleccion. Se debe diseñar el json que se guardará en ella.


2-Frontend:
a) El analisis y opiniones de expertos debe devolverse a una MiniApp de Telegram (indicar los pasos a realizar para crear la mini app).

b) El codigo de la miniapp se va a hostear en vercel de manera gratuita. Y debe invocar a Lambda del backend.



