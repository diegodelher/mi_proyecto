'''
from flask import Flask, request, render_template, send_file
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import io
import requests

app = Flask(__name__)

# Configuración de la API de Google Cloud Vision
API_KEY_PATH = 'C:\\Users\\diego\\keys\\solar-virtue-432107-n3-ddebe8916ccf.json'
credentials = service_account.Credentials.from_service_account_file(API_KEY_PATH)
client = vision.ImageAnnotatorClient(credentials=credentials)

# Ruta principal para el formulario de carga de imagen
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar la carga de imagen y búsqueda de imágenes similares
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        image = file.read()
        response = find_similar_images(image)
        return render_template('results.html', similar_images=response)

def find_similar_images(image_content):
    image = vision.Image(content=image_content)
    response = client.web_detection(image=image)
    similar_images = []

    if response.web_detection.visually_similar_images:
        for similar_image in response.web_detection.visually_similar_images:
            similar_images.append(similar_image.url)

    return similar_images

#def find_similar_images(image_content):
#    image = vision.Image(content=image_content)
#    response = client.web_detection(image=image)
#    similar_images = []

#    if response.web_detection.full_matching_images:
#        for match in response.web_detection.full_matching_images:
#            # La URL de la página web es la misma que la URL de la imagen
#            # en el contexto de Google Cloud Vision. Debes considerar usar un campo adecuado
#            # para identificar el enlace a la página.
#            similar_images.append({
#                'image_url': match.url,
#                'page_url': match.url  # Aquí puedes usar el URL de la página web si está disponible
#            })

#    elif response.web_detection.partial_matching_images:
#        for match in response.web_detection.partial_matching_images:
#            # Similar al anterior, usa el URL de la página web
#            similar_images.append({
#                'image_url': match.url,
#                'page_url': match.url  # Aquí puedes usar el URL de la página web si está disponible
#            })
#
#    return similar_images


# Ruta para servir archivos de imagen descargables
@app.route('/download/<path:url>')
def download(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica si hubo un error en la solicitud
        
        img = Image.open(io.BytesIO(response.content))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name='image.png')
    except requests.exceptions.RequestException as e:
        return f"Error al descargar la imagen: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
'''



'''
from flask import Flask, request, render_template, send_file
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import io
import requests

app = Flask(__name__)

# Configuración de la API de Google Cloud Vision
API_KEY_PATH = 'C:\\Users\\diego\\keys\\solar-virtue-432107-n3-ddebe8916ccf.json'
credentials = service_account.Credentials.from_service_account_file(API_KEY_PATH)
client = vision.ImageAnnotatorClient(credentials=credentials)

# Configuración de la Google Custom Search API
api_key = 'AIzaSyDttGl8wRV_m2LQwdRlrcuqws284jnteBo'  # Reemplaza con tu clave de API
search_engine_id = '6456661277fa84cd1'  # Reemplaza con tu ID del motor de búsqueda

# Ruta principal para el formulario de carga de imagen
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar la carga de imagen y búsqueda de imágenes similares
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        image_content = file.read()
        similar_images = find_similar_images(image_content)
        product_details = detect_and_get_product_details(image_content)
        
        print("Product Details in Upload Route:", product_details)  # Añade este print para depuración
        
        return render_template('results.html', similar_images=similar_images, product_details=product_details)

def find_similar_images(image_content):
    image = vision.Image(content=image_content)
    response = client.web_detection(image=image)
    similar_images = []

    if response.web_detection.visually_similar_images:
        for similar_image in response.web_detection.visually_similar_images:
            similar_images.append({'image_url': similar_image.url, 'page_url': similar_image.url})

    return similar_images

def detect_and_get_product_details(image_content):
    image = vision.Image(content=image_content)
    response = client.label_detection(image=image)
    labels = response.label_annotations

    product_details = []
    for label in labels:
        if 'product' in label.description.lower() or 'item' in label.description.lower():
            product_name = label.description
            details = search_google_images(product_name, api_key, search_engine_id)
            product_details.extend(details)  # Usa extend para aplanar la lista de detalles

    print(f"Detected Labels: {labels}")  # Añade este print para depuración
    print(f"Product Details: {product_details}")  # Añade este print para depuración

    return product_details


def search_google_images(query, api_key, search_engine_id):
    search_url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': search_engine_id,
        'searchType': 'image'
    }

    response = requests.get(search_url, params=params)
    print(f"Google API Response Status: {response.status_code}")
    print(f"Google API Response Content: {response.text}")

    if response.status_code == 200:
        search_results = response.json()
        items = search_results.get('items', [])
        product_details = []
        for item in items:
            title = item.get('title', 'No Title')
            link = item.get('link', 'No Link')
            snippet = item.get('snippet', 'No Description')
            product_details.append({
                'title': title,
                'link': link,
                'snippet': snippet
            })
        print(f"Product Details: {product_details}")  # Añade este print para depuración
        return product_details
    else:
        return []


# Ruta para servir archivos de imagen descargables
@app.route('/download/<path:url>')
def download(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica si hubo un error en la solicitud
        
        img = Image.open(io.BytesIO(response.content))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name='image.png')
    except requests.exceptions.RequestException as e:
        return f"Error al descargar la imagen: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
'''
from flask import Flask, request, render_template, send_file
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import io
import requests
import logging
import os

app = Flask(__name__)

# Configuración de las credenciales de Google Cloud
credentials_url = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if credentials_url:
    # Descargar el archivo JSON desde la URL pública
    response = requests.get(credentials_url)
    response.raise_for_status()  # Lanza una excepción si la descarga falla

    # Guardar el archivo en el sistema de archivos local temporalmente
    with open('credentials.json', 'wb') as f:
        f.write(response.content)

    # Configuración de las credenciales
    credentials = service_account.Credentials.from_service_account_file('credentials.json')
else:
    # Usa el archivo local si ya está disponible (opcional)
    credentials = service_account.Credentials.from_service_account_file('credentials.json')

client = vision.ImageAnnotatorClient(credentials=credentials)

# Configuración de la Google Custom Search API
api_key = os.getenv('GOOGLE_API_KEY')
search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        image_content = file.read()
        similar_images = find_similar_images(image_content)
        product_details = detect_and_get_product_details(image_content)
        labels_and_objects = detect_labels_and_objects(image_content)
        
        logger.info("Product Details in Upload Route: %s", product_details)
        logger.info("Labels and Objects: %s", labels_and_objects)
        
        return render_template('results.html', similar_images=similar_images, 
                               product_details=product_details, 
                               labels_and_objects=labels_and_objects)

def find_similar_images(image_content):
    try:
        image = vision.Image(content=image_content)
        response = client.web_detection(image=image)
        similar_images = []

        if response.web_detection.visually_similar_images:
            for similar_image in response.web_detection.visually_similar_images:
                similar_images.append({'image_url': similar_image.url, 'page_url': similar_image.url})

        return similar_images
    except Exception as e:
        logger.error("Error finding similar images: %s", e)
        return []

def detect_and_get_product_details(image_content):
    try:
        image = vision.Image(content=image_content)
        response = client.label_detection(image=image)
        labels = response.label_annotations

        product_details = []
        for label in labels:
            if 'product' in label.description.lower() or 'item' in label.description.lower():
                product_name = label.description
                details = search_google_images(product_name, api_key, search_engine_id)
                product_details.extend(details)

        logger.info("Detected Labels: %s", labels)
        logger.info("Product Details: %s", product_details)

        return product_details
    except Exception as e:
        logger.error("Error detecting and getting product details: %s", e)
        return []

def detect_labels_and_objects(image_content):
    try:
        image = vision.Image(content=image_content)
        response = client.label_detection(image=image)
        labels = response.label_annotations
        
        # Object Localization
        obj_response = client.object_localization(image=image)
        objects = obj_response.localized_object_annotations

        detected_labels = [{'description': label.description, 'score': label.score} for label in labels]
        detected_objects = [{'name': obj.name, 'score': obj.score} for obj in objects]

        return {
            'labels': detected_labels,
            'objects': detected_objects
        }
    except Exception as e:
        logger.error("Error detecting labels and objects: %s", e)
        return {'labels': [], 'objects': []}

def search_google_images(query, api_key, search_engine_id):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': search_engine_id,
        'searchType': 'image'
    }

    response = requests.get(search_url, params=params)
    print(f"Google API Response Status: {response.status_code}")
    print(f"Google API Response Content: {response.text}")

    if response.status_code == 200:
        search_results = response.json()
        items = search_results.get('items', [])
        product_details = []
        for item in items:
            title = item.get('title', 'No Title')
            link = item.get('link', 'No Link')
            snippet = item.get('snippet', 'No Description')
            thumbnail = item.get('image', {}).get('thumbnailLink', 'No Thumbnail')
            product_details.append({
                'title': title,
                'link': link,
                'snippet': snippet,
                'thumbnail': thumbnail
            })
        print(f"Product Details: {product_details}")
        return product_details
    else:
        return []


@app.route('/download/<path:url>')
def download(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        img = Image.open(io.BytesIO(response.content))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name='image.png')
    except requests.exceptions.RequestException as e:
        logger.error("Error downloading the image: %s", e)
        return f"Error al descargar la imagen: {str(e)}", 500

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)

