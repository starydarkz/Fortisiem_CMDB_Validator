""" Version: 1.0  | Created By: StaryDarkz  | Telegram: https://t.me/StaryDarkz """

import sys,re, base64, urllib.request, urllib.parse, urllib.error, ssl
from xml.dom.minidom import Node, parseString, parse
import xml.etree.ElementTree as ET
from colorama import Fore, init
from os import listdir, system, popen, path
import time, calendar, json, httplib2
import getpass


#----Funciones Generales
def read_list(input):
    txt = open(input, "r")
    resultado = []
    for element in txt:
        if "\n" in element:
            element = element.replace("\n", "")
        resultado.append(element)
    return resultado

def save_results(data):
    """ Guardar resultados finales """
    print (data)
    file = open("resultado.csv", "w")
    file.write(data)

def parse_xml(xml_data):

    cmdb = {}

    try:
        # Parsear el XML
        root = ET.fromstring(xml_data)

        for device in root.findall(".//device"):
            #print (device.text)
            device_ip = device.find("accessIp").text
            device_name = device.find("name").text
            flag_approve = device.find("approved").text
            
            cmdb[device_ip] = [device_name,flag_approve]

        return cmdb
    except ET.ParseError as e:
        print(f"Error al parsear el XML: {e}")

def clearwindow():
    ''' Esta funcion limpia la ventana'''
    from os import name, system
    if name == 'nt':
        system("cls")
    else:
        system("clear")

#Variables de Configuracion
clearwindow()
print ("Login CMDB Validator:\n\n")
ip_siem = input("IP FortiSIEM:\n-->")
username = input("Username FortiSIEM (ej: super/user):\n-->")
password =  getpass.getpass("Password FortiSIEM:\n-->")
max_time = int(input("LastEvent Max Hours: \n-->"))
clearwindow()

#----Funciones de extraccion de CMDB
def getCMDBInfo(appServer=ip_siem, user=username, password=password):
    base64_bytes = base64.encodebytes((user + ':' + password).encode())
    auth = 'Basic %s' % base64_bytes.decode()

    url = 'https://' + appServer + '/phoenix/rest/cmdbDeviceInfo/devices'
    request = urllib.request.Request(url)
    request.add_header('Authorization', auth.rstrip())
    request.add_header('User-Agent', 'Python-urllib2/2.7')
    request.get_method = lambda: 'GET'
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(debuglevel=False, context=ctx))
        urllib.request.install_opener(opener)
        handle = urllib.request.urlopen(request)
        outXML = handle.read()
        return (outXML.decode())
    except urllib.error.HTTPError as e:
        if (e.code != 204):
            print (e)



#----FUnciones de extraccion de eventos
def extrat_data_status(xml_string):
    query = ET.fromstring(xml_string).find('./result/progress').text
    return int(query)

def extrat_data_query(xml):
    query = (ET.fromstring(xml).get('requestId'))
    timestamp = ET.fromstring(xml).find('./result/expireTime').text
    resultado = f"{query},{timestamp}"
    return resultado


def dumpXML(xmlList):
    param = []
    for xml in xmlList:
        doc = parseString(xml.encode('ascii', 'xmlcharrefreplace'))
    for node in doc.getElementsByTagName("events"):
        for node1 in node.getElementsByTagName("event"):
            mapping = {}
            for node2 in node1.getElementsByTagName("attributes"):
                for node3 in node2.getElementsByTagName("attribute"):
                    itemName = node3.getAttribute("name")
                    for node4 in node3.childNodes:
                        if node4.nodeType == Node.TEXT_NODE:
                            message = node4.data
                            if '\n' in message:
                                message = message.replace('\n', '')
                            mapping[itemName] = message
            param.append(mapping)
    return param

def select_query(input_time, ip):

    timestamp_now = int(time.time())

    custom_time = 3600 * input_time # 1 hora
    
    time_start = timestamp_now - custom_time
    time_end = timestamp_now - custom_time + 3600

    last_event = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Reports>
    <Report baseline="" rsSync="">
        <Name>Incident Notification Count</Name>
        <Description> Total de Notificaciones con email alert especificado</Description>
        <CustomerScope groupByEachCustomer="false">
        </CustomerScope>
        <SelectClause>
            <AttrList>extEventRecvProto,LAST(phRecvTime)</AttrList>
        </SelectClause>
        <OrderByClause>
            <AttrList>COUNT(*) DESC</AttrList>
        </OrderByClause>
        <PatternClause window="3600">
            <SubPattern id="1164394" name="Filter_OVERALL_STATUS">
                <SingleEvtConstr>(reptDevIpAddr = {ip} AND eventType NOT CONTAIN "PH_")</SingleEvtConstr>
                <GroupByAttr>extEventRecvProto</GroupByAttr>
            </SubPattern>
        </PatternClause>
        <userRoles>
            <roles custId="2001">1169250</roles>
        </userRoles>
        <SyncOrgs/><ReportInterval>
            <Low>{time_start}</Low>
            <High>{time_end}</High>error
        </ReportInterval>
        <TrendInterval>auto</TrendInterval>
        <TimeZone/>
    </Report>
    </Reports>"""
    
    return last_event


def get_queryfromsiem(ip_siem, user, password, xml_query):

    url = "https://" + ip_siem + ":443/phoenix/rest/query/"
    urlfirst = url + "eventQuery"
    
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    h.add_credentials(user, password)
    
    header = {'Content-Type': 'text/xml'}
    
    doc = parseString(xml_query)
    t = doc.toxml()

    if '<DataRequest' in t:
        t1 = t.replace("<DataRequest", "<Reports><Report")
    else:
        t1 = t
    if '</DataRequest>' in t1:
        t2 = t1.replace("</DataRequest>", "</Report></Reports>")
    else:
        t2 = t1

    resp, content = h.request(urlfirst, "POST", t2, header)
    queryId = content.decode("utf-8")
    if "xml version" in queryId:
        queryId = extrat_data_query(queryId)
        
    if 'error code="255"' in queryId:
        print ("Query Error, check sending XML file.")
        exit()

    urlSecond = url + "progress/" + queryId
    if resp['status'] == '200':
        resp, content = h.request(urlSecond)

    else:
        print ("appServer doesn't return query. Error code is %s" % resp['status'] )
        exit()


    while True:
        resp, content = h.request(urlSecond)
        try: 
            progreso = extrat_data_status(content)
            #print (progreso)
            if progreso == 100:
                break
        except:
            while content.decode("utf-8") != '100':
                resp, content = h.request(urlSecond)
            break

    outXML = []
   
    
    urlFinal = url + 'events/' + queryId + '/0/1000'
    resp, content = h.request(urlFinal)
    
    #print (resp, "\n\n", content)

    if content != '':
        outXML.append(content.decode("utf-8"))

    p = re.compile('totalCount="\d+"')
    mlist = p.findall(content.decode())
    
    
    if mlist[0] != '':
        mm = mlist[0].replace('"', '')
        m = mm.split("=")[-1]
        num = 0
        if int(m) > 1000:
            num = int(m) / 1000
            if int(m) % 1000 > 0:
                num += 1
        if num > 0:
            for i in range(num):
                urlFinal = url + 'events/' + queryId + '/' + str((i + 1) * 1000) + '/1000'
                resp, content = h.request(urlFinal)
                if content != '':
                    outXML.append(content.decode("utf-8"))
    else:
        print ("no info in this report.")
        return "Error"
    data = dumpXML(outXML)
    return data



def getLastEvent(ip, max_time = max_time):
    resultado = ""
    for element in range(1,max_time+1):
        data = get_queryfromsiem(ip_siem, username, password, select_query(element,ip))
        if len(data) != 0: # Si trae data terminar de buscar en mas tiempo
            break
    
    if len(data) == 0: 
        return "N\A"
    
    for element in data:
        
        last_event = element["LAST(phRecvTime)"]
        try:
            monitor = element["extEventRecvProto"]
        except:
            monitor = "Unknown"
        resultado = resultado + f"{monitor}={last_event}|"

    return resultado


def menu():
    clearwindow()
    rojo = Fore.RED
    azul = Fore.LIGHTCYAN_EX
    input_user = input(rojo + """

          *     (                                                           
   (    (  `    )\ )    (                 (       (             )           
   )\   )\))(  (()/(  ( )\   (   (     )  )\ (    )\ )    )  ( /(      (    
 (((_) ((_)()\  /(_)) )((_)  )\  )\ ( /( ((_))\  (()/( ( /(  )\()) (   )(   
 )\\"""+azul+"""___"""+rojo+""" ("""+azul+"""_"""+rojo+"""()(("""+azul+"""_"""+rojo+""")("""+azul+"""_"""+rojo+"""))"""+azul+"""_"""+rojo+""" (("""+azul+"""_"""+rojo+""")"""+azul+"""_"""+rojo+"""  (("""+azul+"""_"""+rojo+""")(("""+azul+"""_"""+rojo+"""))(_))"""+azul+""" _ """+rojo+"""(("""+azul+"""_"""+rojo+""")  (("""+azul+"""_"""+rojo+""")))(_"""+rojo+"""))("""+azul+"""_"""+rojo+"""))/  )\ (()\  
(("""+azul+"""/ __||  \/  | |   \ | _ ) \ \ / /"""+rojo+"""(("""+azul+"""_"""+rojo+""")"""+azul+"""_ | | (_)  _| |"""+rojo+"""(("""+azul+"""_"""+rojo+""")"""+azul+"""_ | |_  """+rojo+"""(("""+azul+"""_"""+rojo+""") (("""+azul+"""_"""+rojo+""")"""+azul+""" 
 | (__ | |\/| | | |) || _ \  \ V / / _` || | | |/ _` |/ _` ||  _|/ _ \| '_| 
  \___||_|  |_| |___/ |___/   \_/  \__,_||_| |_|\__,_|\__,_| \__|\___/|_|   
                                                                            

    
    Selecciona una de las opciones:

    1 | Validar CMDB a partir de un listado
    2 | Extraer equipos que no envian eventos
    3 | Extraer toda la CMDB y la ultima vez que enviaron
    
    -->""")

    return input_user                                                                

                                                                                                       


def main():
    
    input_user = menu()


    data_fortisiem = getCMDBInfo()
    cmdb = parse_xml(data_fortisiem)
    num_cmdb = len(cmdb)
    count = 0
    if input_user == "1": #Validar CMDB a partir de un listado
        resultado = "IP del equipo, Nombre del equipo, Aprobado en el SIEM, Monitor\n"

        filename = input("Ruta del archivo: \n-->")
        lista_cliente = read_list(filename)
        
        
        for element_cliente in lista_cliente:
            """ Crea el resultado en base a la lista del cliente"""
            
            if element_cliente in cmdb:

                last_event = getLastEvent(element_cliente)
                resultado = resultado + (f"{element_cliente},{cmdb[element_cliente][0]},{cmdb[element_cliente][1]},{last_event}\n")

            else:
                resultado = resultado + (f"{element_cliente},HOST-{element_cliente},False,No integrado al SIEM\n")
    
    elif input_user == "2": #Extraer equipos que no envian eventos
        print ("Analizando equipos...")
        resultado = "IP del equipo, Nombre del equipo, Monitor\n"
        for element in cmdb:
            count = count + 1
            clearwindow()
            print ("[SELECCIONADO] | Extraer equipos que no envian eventos\n\nAnalizando equipos...")
            print (f"Status: {count}/{num_cmdb}")
            last_event = getLastEvent(element)
            if last_event == "N\A":
                resultado = resultado + (f"{element},{cmdb[element][0]},{last_event}\n")
    
    elif input_user == "3": #Extraer toda la CMDB y la ultima vez que enviaron
        
        resultado = "IP del equipo, Nombre del equipo, Monitor\n"
        for element in cmdb:
            count = count + 1
            clearwindow()
            print ("[SELECCIONADO] | Extraer toda la CMDB y la ultima vez que enviaron\n\nAnalizando equipos...")
            print (f"Status: {count}/{num_cmdb}")
            last_event = getLastEvent(element)
            resultado = resultado + (f"{element},{cmdb[element][0]},{last_event}\n")
    save_results (resultado)

main()