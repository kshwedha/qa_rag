## ASK-QUESTION

```
curl -X POST "http://0.0.0.0:5001/api/question"      -H "Content-Type: application/json"      -d '{"question": "What is Quality?", "document_id":"725978c0-870e-40ea-9736-9fab390c31f4", "top_k": 5}'
{
  "answer": "identify the defects and provide quality product to end user",
  "confidence": 0.023296425119042397,
  "context": "[Prepared By: Kamal Subramani ] Page 1 1. TESTING \uf0d8 It helps to identify the defects and provide quality product to end user . \uf0d8 It will happen D (Development) to D (Delivery to End User).",
  "sources": [
    {
      "id": "725978c0-870e-40ea-9736-9fab390c31f4",
      "similarity": 0.3350039224327781,
      "title": "manual-testing.pdf"
    }
  ]
}
```

## UPLOAD

```
curl -X POST "http://0.0.0.0:5001/api/documents"      -H "Content-Type: multipart/form-data"      -F "file=@/Users/maath/Downloads/manual-testing.pdf"      -F "metadata={\"author\": \"me\", \"title\": \"manual testing\"}"
```
