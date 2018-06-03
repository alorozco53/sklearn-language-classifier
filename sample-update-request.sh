# actualizar dataset
curl -X POST -H "Content-Type: application/json" \
	 -d "$(cat sample-req.json)" \
	 localhost:4000/update

# hacer una petición
curl -X POST -H "Content-Type: application/json" \
	 -d '{"query": "Chatbot FACEBOOK web framework", "k": "4"}' \
	 localhost:4000
