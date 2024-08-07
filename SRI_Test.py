from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time
import requests
from tqdm import tqdm
import datetime

# Variables de configuración
anio = '2023'
mes = '1'
dia = '0'
tipo_comprobante = 'FACTURA'
RUC = '1312478686'
CLAVE = 'EjGh2019'

# Función para resolver el captcha usando 2Captcha
def resolve_captcha():
    url_in = "https://2captcha.com/in.php"
    payload_in = {
        'pageurl': 'https://srienlinea.sri.gob.ec/tuportal-internet/accederAplicacion.jspa?redireccion=57&idGrupo=55',
        'key': 'd6719a36f9871097e45bcd72473e7682',
        'method': 'userrecaptcha',
        'googlekey': '6Lc6rokUAAAAAJBG2M1ZM1LIgJ85DwbSNNjYoLDk'
    }

    response_in = requests.post(url_in, data=payload_in)
    captcha_id = response_in.text.split('|')[1]
    print(f"Captcha ID: {captcha_id}")

    url_res = f"https://2captcha.com/res.php?key=d6719a36f9871097e45bcd72473e7682&action=get&id={captcha_id}&json=1"

    captcha_response = None
    for i in tqdm(range(15), desc="Esperando resolución del captcha", unit="intento"):
        response_res = requests.get(url_res)
        result = response_res.json()
        if result['status'] == 1:
            captcha_response = result['request']
            print(f"\nCaptcha Resuelto: {captcha_response}")
            break
        else:
            time.sleep(3)

    if captcha_response is None:
        print("No se pudo resolver el captcha después de 15 intentos.")
        exit()

    return captcha_response

# Configuración de la ruta de descarga
download_folder = 'C:\\ComprobantesDescargadosSRI'
current_date = datetime.datetime.now().strftime("%Y%m%d")
download_path = f"{download_folder}\\{RUC}.{current_date}{tipo_comprobante}.txt"

chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_folder,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Ruta al driver de Chrome
chrome_driver_path = 'C:\\SRIdescargaBBF\\driver\\chromedriver.exe'

# Configuración del servicio de ChromeDriver
service = Service(chrome_driver_path)

# Opciones para el navegador
chrome_options.add_argument('--start-maximized')

try:
    # Inicializar el navegador
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Maximizar el navegador al abrirlo
    driver.maximize_window()

    # Navegar a la página web del SRI
    driver.get('https://srienlinea.sri.gob.ec/sri-en-linea/inicio/NAT')

    # Esperar a que la página cargue y el enlace sea visible
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a.sri-tamano-link-iniciar-sesion'))
    )

    # Hacer clic en el enlace "Iniciar sesión"
    login_link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.sri-tamano-link-iniciar-sesion'))
    )
    actions = ActionChains(driver)
    actions.move_to_element(login_link).click().perform()
    print("Se hizo clic en 'Iniciar sesión'.")

    # Ingresar el RUC en el campo de entrada de usuario
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'usuario'))
    )
    user_input = driver.find_element(By.ID, 'usuario')
    user_input.send_keys(RUC)
    print("Se ingresó el RUC en el campo de entrada de usuario.")

    # Ingresar la clave en el campo de entrada de contraseña
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'password'))
    )
    password_input = driver.find_element(By.ID, 'password')
    password_input.send_keys(CLAVE)
    print("Se ingresó la clave en el campo de entrada de contraseña.")

    # Hacer clic en el botón de ingreso
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'kc-login'))
    )
    login_button = driver.find_element(By.ID, 'kc-login')
    actions.move_to_element(login_button).click().perform()
    print("Se hizo clic en el botón 'Ingresar'.")

    # Validar que la página haya cargado completamente después del inicio de sesión
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'label.titulo-campo.porciento.nombre-contribuyente'))
    )
    print("Página cargada completamente después del inicio de sesión.")

    # Navegar a la nueva URL dentro de la misma sesión
    driver.get('https://srienlinea.sri.gob.ec/tuportal-internet/accederAplicacion.jspa?redireccion=57&idGrupo=55')
    print("Se navegó a la nueva URL.")

    # Esperar a que el botón de consulta esté visible
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'btnRecaptcha'))
    )

    # Seleccionar AÑO, MES, DÍA y TIPO DE COMPROBANTE
    try:
        # Seleccionar el año
        year_select = Select(driver.find_element(By.ID, 'frmPrincipal:ano'))
        year_select.select_by_value(anio)

        # Seleccionar el mes
        month_select = Select(driver.find_element(By.ID, 'frmPrincipal:mes'))
        month_select.select_by_value(mes)

        # Seleccionar el día 'Todos'
        day_select = Select(driver.find_element(By.ID, 'frmPrincipal:dia'))
        day_select.select_by_value(dia)

        # Seleccionar el tipo de comprobante
        type_select = Select(driver.find_element(By.ID, 'frmPrincipal:cmbTipoComprobante'))
        type_select.select_by_visible_text(tipo_comprobante)

        print("Seleccionados año, mes, día y tipo de comprobante.")
    except Exception as e:
        print(f"Error seleccionando las opciones: {e}")

    # Resolver el captcha usando 2Captcha
    captcha_solution = resolve_captcha()
    print(captcha_solution)
    driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_solution}";')
    print("Se insertó la respuesta del captcha en el campo oculto.")
    driver.execute_script("rcBuscar("");")
    print("Se ejecutó rcBuscar.")

    # Esperar y hacer clic en el enlace "Descargar Reporte"
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'frmPrincipal:lnkTxtlistado'))
    )

    # Manejar elemento superpuesto si existe
    try:
        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.ID, 'dlgpopStatusPrime'))
        )
        print("Elemento superpuesto desaparecido.")
    except Exception as e:
        print(f"Error esperando la desaparición del elemento superpuesto: {e}")

    download_link = driver.find_element(By.ID, 'frmPrincipal:lnkTxtlistado')
    driver.execute_script("arguments[0].click();", download_link)
    print("Se hizo clic en el enlace 'Descargar Reporte'.")

    # Esperar un poco para asegurar que el archivo se descargue
    time.sleep(10)

    print(f"Proceso de descarga completado. Archivo descargado en: {download_path}")
finally:
    driver.quit()
