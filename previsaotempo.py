import requests  # fazer requisições
import json  # ler dados em json e convertê-los para python
from datetime import date
import urllib.parse
import pprint  # visualizar as informações de forma mais clara

accuweatherAPIKey = 'l9BlQs8GQ0lulFE2H5a60asaZGATJlZ0'
mapboxToken =  "pk.eyJ1Ijoid2VzbGV5MDAiLCJhIjoiY2t0OHIzeGI2MTR4dTJvbnI2YXU1ZzdseiJ9.7_qUHcXm2omdvyR8fxwq9A"
dias_semana = ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]


def pegarCoordenadas():
    r = requests.get(
        "http://www.geoplugin.net/json.gp")  # Obter localização do usuário com o geoPlugin API (geoplugin.com)

    if (r.status_code != 200):
        print("Não foi possível obter a localização.")
        return None
    else:
        try:
            localizacao = json.loads(r.text)  # dados convertidos para formato dicionário
            coordenadas = {}
            coordenadas["lat"] = localizacao["geoplugin_latitude"]
            coordenadas["long"] = localizacao["geoplugin_longitude"]
            return coordenadas
        except:
            return None


def pegarCodigoLocal(lat, long):
    locationAPIUrl = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/" \
                     + "search?apikey=" + accuweatherAPIKey \
                     + "&q=" + lat + "%2C%20" + long + "&language=pt-br"

    r = requests.get(locationAPIUrl)
    if (r.status_code != 200):
        print("Não foi possível obter o código do local.")
        return None
    else:
        try:
            locationResponse = json.loads(r.text)
            infoLocal = {}
            infoLocal["nomeLocal"] = locationResponse["LocalizedName"] + ", " \
                                     + locationResponse["AdministrativeArea"]["LocalizedName"] + ". " \
                                     + locationResponse["Country"]["LocalizedName"]
            infoLocal["codigoLocal"] = locationResponse["Key"]
            return infoLocal
        except:
            return None


def pegarTempoAgora(codigoLocal, nomeLocal):
    currentConditionsAPIUrl = "http://dataservice.accuweather.com/currentconditions/v1/" \
                              + codigoLocal + "?apikey=" + accuweatherAPIKey \
                              + "&language=pt-br"

    r = requests.get(currentConditionsAPIUrl)
    if (r.status_code != 200):
        print("Não foi possível obter o clima atual.")
        return None
    else:
        try:
            currentConditionsResponse = json.loads(r.text)
            infoClima = {}
            infoClima["textoClima"] = currentConditionsResponse[0]["WeatherText"]
            infoClima["temperatura"] = currentConditionsResponse[0]["Temperature"]["Metric"]["Value"]
            infoClima["nomeLocal"] = nomeLocal
            return infoClima
        except:
            return None


def pegarPrevisaoCincoDias(codigoLocal):
    DailyAPIUrl = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" \
                  + codigoLocal + "?apikey=" + accuweatherAPIKey \
                  + "&language=pt-br&metric=true"
    r = requests.get(DailyAPIUrl)
    if (r.status_code != 200):
        print("Não foi possível obter a previsão para os próximos 5 dias.")
        return None
    else:
        try:
            DailyResponse = json.loads(r.text)
            infoClima5Dias = []
            for dia in DailyResponse["DailyForecasts"]:
                climaDia = {}
                climaDia["max"] = dia["Temperature"]["Maximum"]["Value"]
                climaDia["min"] = dia["Temperature"]["Minimum"]["Value"]
                climaDia["clima"] = dia["Day"]["IconPhrase"]
                diaSemana = int(date.fromtimestamp(dia["EpochDate"]).strftime("%w"))
                climaDia["dia"] = dias_semana[diaSemana]
                infoClima5Dias.append(climaDia)
            return infoClima5Dias
        except:
            return None


def mostrarPrevisao(lat, long):
    try:
        local = pegarCodigoLocal(lat, long)
        climaAtual = pegarTempoAgora(local["codigoLocal"], local["nomeLocal"])
        print("Clima atual em " + climaAtual["nomeLocal"])
        print(climaAtual["textoClima"])
        print("Temperatura: " + str(climaAtual["temperatura"]) + "\xb0" + "C")
    except:
        print("Erro ao obter o clima atual")

    opcao = (input("Deseja ver a previsão para os próximos dias? (s ou n): ")).lower()

    if opcao == "s":
        print("\nClima para hoje e para os próximos dias:\n")

        try:
            previsao5dias = pegarPrevisaoCincoDias(local["codigoLocal"])
            for dia in previsao5dias:
                print(dia["dia"])
                print("Mínima: " + str(dia["min"]) + "\xb0" + "C")
                print("Máxima: " + str(dia["max"]) + "\xb0" + "C")
                print("Clima: " + dia["clima"])
                print("--------------------------------")
        except:
            print("Erro ao obter a previsão para os próximos dias")


def pesquisarLocal(local):
    _local = urllib.parse.quote(local)
    # print(_local)
    mapboxGeocodeUrl = "https://api.mapbox.com/geocoding/v5/mapbox.places/" \
                       + _local + ".json?access_token=" + mapboxToken
    r = requests.get(mapboxGeocodeUrl)
    if (r.status_code != 200):
        print("Não foi possível obter o clima atual.")
        return None
    else:
        try:
            MapboxResponse = json.loads(r.text)
            coordenadas = {}
            coordenadas["long"] = str(MapboxResponse["features"][0]["geometry"]["coordinates"][0])
            coordenadas["lat"] = str(MapboxResponse["features"][0]["geometry"]["coordinates"][1])

            return coordenadas
        except:
            print("Erro na pesquisa de local.")


try:
    coordenadas = pegarCoordenadas()
    mostrarPrevisao(coordenadas["lat"], coordenadas["long"])

    continuar = "s"

    while continuar == "s":
        continuar = input("Deseja consultar a previsão de outro local? (s ou n): ").lower()
        if continuar != "s":
            break
        local = input("Digite a cidade e o estado: ")
        try:
            coordenadas = pesquisarLocal(local)
            mostrarPrevisao(coordenadas["lat"], coordenadas["long"])
        except:
            print("Não foi possível obter a previsão para este local.")

except:
    print("Erro ao processar a solicitação. Entre em contato com o suporte.")

    # COMENTÁRIOS

# Trabalhando com dados em JSON em Python
# O comando 'json.loads(r.text)', acima, converte os dados de json para um dicionário em Python
# Instalação com cmd (windows+R) o módulo pprint - pip install pprint
# Para ver os dados de uma forma mais clara, use o comando "print(pprint.pprint(localizacao))"

# Para usar a api do accuweather é preciso se registrar.
# 1- acesse o site https://developer.accuweather.com/
# 2-clique em "register
# 3-Será enviado um email
# 4-Definir senha
# 5-Clicar em "My Apps"
# 6-"+ Add new app"
# 7- Preencher formulário e criar o app
# 8- Clicar no nome do app
# 9- Copiar a "API Key"
# 10-Clicar em "API Reference"
# 11-O clima atual é dado pela "Current Conditions API"

# Para obter o código da localidade:
# 1-Clicarem "API Reference"
# 2- "Locations API"
# 3- "Geoposition Search"
# 4- Obter o código da localidade (chave "key")
# 5-Clicar em "cURL" para descubrir o endereço HTTP a ser usado para fazer a requisição
# 6- Preparar a URL, substituindo a APIKey pela variável correspondente
# bem como a latitude e a longitude

# xb0 é o símbolo para "º" - graus
