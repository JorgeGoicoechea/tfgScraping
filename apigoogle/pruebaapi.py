import requests

def get_company_website(company_name, api_key):
    # Define la URL de la API de Google
    api_url = "https://www.googleapis.com/customsearch/v1"
    
    # Parámetros de la búsqueda
    params = {
        "key": api_key,
        "cx": "YOUR_CUSTOM_SEARCH_ENGINE_ID",  # Reemplaza con tu ID de motor de búsqueda personalizado
        "q": company_name
    }

    # Realiza la solicitud a la API de Google
    response = requests.get(api_url, params=params)

    # Procesa la respuesta JSON
    data = response.json()

    # Verifica si se encontraron resultados
    if "items" in data:
        first_result = data["items"][0]
        website = first_result["link"]
        return website
    else:
        return None

# Tu clave de API de Google
api_key = "TU_CLAVE_DE_API_AQUI"

company_name = input("Ingrese el nombre de la empresa: ")
website = get_company_website(company_name, api_key)

if website:
    print(f"El sitio web de {company_name} es: {website}")
else:
    print(f"No se encontraron resultados para {company_name}")