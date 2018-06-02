# Base Sci-kit Learn language classifier

---

## Para el hackathon de Wizeline...

Para hacer una consulta al servicio, hay que adjuntar un `JSON` de la forma

```json
{"query": <TEXTO_EN_LENGUAJE_NATURAL>,
 "k": <NÚMERO_DE_TÍTULOS_DE_REPOS_MÁS_SIMILARES_A_REGRESAR>
}
```

El objeto `k` indica que el servicio debe de devolver los _k_ repos más similares,
por lo tanto, es un entero positivo y es un parámetro _opcional_.

La estructura de una petición `POST` sería la siguiente:

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"query": "<QUERY>", "k": "<K>"}' \
localhost:4000
```

Hay un servicio corriendo en https://2f23e855.ngrok.io, por lo tanto,
la petición anterior se puede reemplazar `localhost:4000` con dicha URL.

También hay una Dockerfile si se desea correr en otro servidor.

Una vez que se hace la petición, el servidor regresa un `JSON` con los `k`
mejores resultados consistiendo en su **ID** de repo y un _score_. Por ejemplo,
si solicitamos los 4 repos más cercanos para la frase `"architecture service feedback api"`,
entonces, nos arrojaría el siguiente `JSON`:

```json
{"SCORE": {"3":0.2199776121,
	       "1":0.2082796948,
		   "4":0.2017049632,
		   "7":0.1854712961
	      }
}
```

donde los números enteros (nombres de objetos) son los IDs de los repos y sus valores
son el score resultante del procesamiento.

(El score es un valor entre 0 y 1.)
