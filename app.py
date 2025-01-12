from flask import Flask, jsonify, render_template, request
import os
from numpy import true_divide
import pandas as pd
import csv
import base64
import json
from urllib.parse import urlparse, parse_qs
from zipfile import ZipFile
from collections import defaultdict
from androguard.core.bytecodes.dvm import DalvikVMFormat
from androguard.core.bytecodes import dvm
from androguard.core.bytecodes.dvm import DalvikVMFormat
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = 'uploads'

def har_to_csv():
    har_file_name = 'upload_har.har'
    har_folder = 'har_file_upload'
    csv_folder = 'uploads'
    csv_file_name = 'uploaded_file.csv'
    har_file_path = os.path.join(har_folder, har_file_name)
    csv_file_path = os.path.join(csv_folder, csv_file_name)

    try:
        with open(har_file_path, "r", encoding="utf-8") as file:
            har_data = json.load(file)

        with open(csv_file_path, "w", newline='', encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)

            csv_writer.writerow([
                "Request URL",
                "Request Method",
                "Request Headers",
                "Request Query Params",
                "Request Body",
                "Response Status",
                "Response Headers",
                "Response Body",
                "Ping (Wait Time)"
            ])

            for entry in har_data.get('log', {}).get('entries', []):
                request = entry.get('request', {})
                response = entry.get('response', {})
                timings = entry.get('timings', {})

                csv_writer.writerow([
                    request.get('url', 'No URL'),
                    request.get('method', 'No Method'),
                    str(request.get('headers', 'No Headers')),
                    str(request.get('queryString', 'No Query Params')),
                    request.get('postData', {}).get('text', 'No Body'),
                    response.get('status', 'No Status'),
                    str(response.get('headers', 'No Headers')),
                    response.get('content', {}).get('text', 'No Body'),
                    timings.get('wait', 'No Wait Time')
                ])

        print(f"CSV file created successfully at {csv_file_path}")
    except Exception as e:
        print(f"Error during HAR to CSV conversion: {e}")

har_to_csv()

@app.route('/', methods=['GET'])
def index():
    url_flags = {
        "GAM_init": [],
        "GAM_load": [],
        "GAM_impression": [],
        "IronSource_init": [],
        "IronSource_load": [],
        "Mtg_init": [],
        "Mtg_bid": [],
        "Mtg_LoadAd": [],
        "Mtg_Impression": [],
        "MAX_load": [],
        "MAX_impression": [],
        "MAX_creative_url": [],
        "vungle_init": [],
        "vungle_load":[],
        "vungle_impression":[],
        "Molloco_creative": [],
        "DigitalTurbine_init": [],
        "DigitalTurbine_load": [],
        "APS_init":[],
        "APS_bid" :[],
        "APS_load":[],
        "APS_impression":[],
        "APS_click":[],
        "Crackle_init":[],
        "CrackleRTB_init":[],
        "CrackleUnity_init":[],
        "GoogleAdbmob_init":[],
        "GoogleAdmob_load":[],
        "GoogleAdmob_click": [],
        "GoogleAdmob_impression":[],
    }

    url_flag_mapping = {
        "GAM_init": [
            "googleads.g.doubleclick.net/ads/favicon", 
            "googleads.g.doubleclick.net/ads/mads",
            "googleads.g.doubleclick.net/ads/getconfig"
        ],
        "GAM_load": [
            "pubads.g.doubleclick/gampad"
        ],
        "GAM_impression": [
            "googleads.g.doubleclick.com/pageAds/adview"
        ],
        "IronSource_init": [
            "o-sdk.mediation.unity3d"
        ],
        "IronSource_load": [
            "gw.mediation.unity3d"
        ],
        "Mtg_init": [
            "configure.rayjump"
        ],
        "Mtg_bid": [
            "hb.mtgglobals"
        ],
        "Mtg_LoadAd": [
            "sg-new-cdn-ssplib-asia-southeast1-c-hb.mtgglobals.com"
        ],
        "Mtg_Impression": [
            "sg01.mtgglobals"
        ],
        "MAX_load": [
            "ms4/1.0/mediate"
        ],
        "MAX_impression": [
            "prod-mediate-events.applovin.com/1.0/event/vimp"
        ],
        "MAX_creative_url": [
            "cdn.jampp.com,assets.applovin.com"
        ],
        "vungle_init": [
            "ads.api.vungle.com",
            "new.ads.vungle.com/api/v5/new",
            "config.ads.vungle.com/config "
        ],
        "vungle_load": [
            "adx.ads.vungle.com/api/v7/ads"
        ],
        "vungle_impression": [
            "events.ads.vungle.com/api/v7/tpat"
        ],
        "Molloco_creative": [
            "cdn-f.adsmoloco.com"
        ],
        "DigitalTurbine_init": [
            "cdn2.inner-active.mobi/ia-sdk-config/"
        ],
        "DigitalTurbine_load": [
            "wv.inner-active.mobi/simpleM2M/clientRequestEnhancedXmlAd"
        ],
        "APS_init": [
            "mads.amazon-adsystem.com"
        ],
        "APS_bid": [
            "aax.amazon-adsystem.com"
        ],
        "APS_load": [
            "ts.amazon-adsystem.com"
        ],
        "APS_impression": [
            "aax-dtb-mobile-geo.amazon-adsystem.com"
        ],
        "APS_click": [
            "aax-eu.amazon-adsystem.com"
        ],
        "Crackle_init": [
            "crackle.co.in/user-module"
        ],
        "CrackleRTB_init": [
            "ra.ctech.works"
        ],
        "CrackleUnity_init": [
            "crackle.co.in/user-module"
        ],
        "GoogleAdmob_init": [
            "googleads.g.doubleclick.net/favicon",
            "googleads.g.doubleclick.net/mads",
            "googleads.g.doubleclick.net/getconfig"
        ],
        "GoogleAdmob_load": [
            "googleads.g.doubleclick.net/mads/gma"
        ],
        "GoogleAdmob_impression": [
            "pagead2.googlesyndication.com/pcs/activeview"
        ],
        "GoogleAdmob_click": [
            "googleads.g.doubleclick.net/aclk",
            "googleadservices.com/pagead/aclk"
        ]
    }

    
    UPLOAD_FOLDER = 'uploads'
    file_name = 'uploaded_file.csv'
    file_path = os.path.join(UPLOAD_FOLDER, file_name)

    
    iu_with_crackle = []
    iu_without_crackle = []


    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        aggregated_flags = url_flags.copy()

        for sspAndPingType, url_Substring_Array in url_flag_mapping.items():
            for url_Substring in url_Substring_Array:
                didFind = False
                for request_url in df['Request URL'].tolist():
                    if url_Substring in request_url:
                        aggregated_flags[sspAndPingType].append(True)
                        didFind = True
                        break
                if not didFind:
                        aggregated_flags[sspAndPingType].append(False)

        print(aggregated_flags['GAM_init'])
        process_response_body(df, iu_with_crackle, iu_without_crackle)
        print("Aggregated Flags: ")
        for flag, value in aggregated_flags.items():
            print(f"{flag}: {value}")

        print(f"iu values with crackle: {iu_with_crackle}")
        print(f"iu values with no crackle: {iu_without_crackle}")
    else:
        print(f"File '{file_name}' not found in folder '{UPLOAD_FOLDER}'.")

    return render_template('new_index.html', flags=aggregated_flags,
                           iu_with_crackle=iu_with_crackle, iu_without_crackle=iu_without_crackle)


    
def process_response_body(df, iu_with_crackle, iu_without_crackle):
    for index, row in df.iterrows():
        request_url = row.get('Request URL', '')
        
        if 'pubads.g.doubleclick.net/gampad/ads' in request_url:
            encoded_response_body = row.get('Response Body', '')
            
            missing_padding = len(encoded_response_body) % 4
            if missing_padding != 0:
                encoded_response_body += "=" * (4 - missing_padding)
            
            try:
                decoded_bytes = base64.b64decode(encoded_response_body)
                decoded_response_body = decoded_bytes.decode('utf-8')
                
                response_json = json.loads(decoded_response_body)
                
                for ad_network in response_json.get('ad_networks', []):
                    class_name = ad_network.get('data', {}).get('class_name', '').lower()
                    
                    parsed_url = urlparse(request_url)
                    query_params = parse_qs(parsed_url.query)
                    iu_values_list = query_params.get('iu', [])
                    
                    if 'crackle' in class_name:
                        iu_with_crackle.extend(iu_values_list)
                    else:
                        iu_without_crackle.extend(iu_values_list)
            
            except base64.binascii.Error:
                print(f"Invalid base64 string for Request URL {request_url}.")
            except json.JSONDecodeError:
                print(f"Decoded response body is not valid JSON for Request URL {request_url}.")
            except Exception as e:
                print(f"Unexpected error processing Request URL {request_url}: {e}")


def calculate_class_size(class_obj):
    total_size = 0

    total_size += len(class_obj.get_name().encode('utf-8'))

    for interface in class_obj.get_interfaces():
        total_size += len(interface.encode('utf-8'))

    for method in class_obj.get_methods():
        if method.get_code():
            total_size += method.get_code().get_length()
        total_size += len(method.get_name().encode('utf-8'))  
        total_size += len(method.get_descriptor().encode('utf-8'))  
    for field in class_obj.get_fields():
        total_size += len(field.get_name().encode('utf-8'))
        total_size += len(field.get_descriptor().encode('utf-8'))  

    return total_size

def get_class_size_from_dex(dex_content, target_class_name):
    dex_obj = dvm.DalvikVMFormat(dex_content)
    total_size = 0
    for class_obj in dex_obj.get_classes():
        if class_obj.get_name().startswith(target_class_name):
            total_size += calculate_class_size(class_obj)
    return total_size

@app.route('/uploadApk', methods=['POST'])
def upload_apk():    
    if 'apkFile' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400
   
    file = request.files['apkFile']

    
    if file.filename == '':
        return jsonify({"message": "No file selected for uploading"}), 400

    if not file.filename.endswith('.apk'):
        return jsonify({"message": "Invalid file type. Only .apk files are allowed."}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(file_path)

    target_ssps = {
        # Inmobi
        'Lcom/inmobi':0.0,
        'Inmobi':0.0,

        # Adster
        'Lcom/adster':0.0,
        'Adster':0.0,

        # IronSource
        'Lcom/ironsource':0.0,
        'Lcom/iab/omid/library/ironsrc':0.0,
        'Lcom/unity3d/ironsourceads':0.0,
        'Lcom/unity3d/mediation':0.0,
        'IronSource':0.0,

        # GAM 
        'Lcom/google/android/gms':0.0,
        'GAM/Admob':0.0,
        
        # Mintegral
        'Lcom/mbridge/msdk':0.0,
        'Lcom/iab/omid/library/mmadbridge':0.0,
        'Mintegral':0.0,

        # Applovin
        'Lcom/applovin':0.0,
        'Lcom/iab/omid/library/applovin':0.0,
        'Applovin':0.0,

        # Unity_Clouds
        'Lcom/unity3d/ads':0.0,
        'Lcom/unity3d/services':0.0,
        'Lcom/iab/omid/library/unity3d':0.0,
        'Lcom/unity3d/scar/adapter/v2000':0.0,
        'Lcom/unity3d/scar/adapter/v2100':0.0,
        'Lcom/unity3d/scar/adapter/v2300':0.0,
        'Lcom/unity3d/scar/adapter/common':0.0,
        'Unity_Clouds':0.0,
        
        # vungle
        'Lcom/iab/omid/library/vungle': 0.0,
        'Lcom/vungle/ads': 0.0,
        'vungle':0.0,
        
        # facebook
        'Lcom/facebook/ads':0.0,
        'Lcom/facebook/infer/annotation':0.0,
        'facebook':0.0,

        # DigitalTurbine/Fyber
        'Lcom/digitalturbine/ignite':0.0,
        'Lcom/fyber/inneractive':0.0,
        'Lcom/fyber/marketplace':0.0,
        'Lcom/iab/omid/library/fyber':0.0,
        'DigitalTurbine/Fyber':0.0,

    }

    with ZipFile(file_path, 'r') as apk_zip:
        for target_ssp in target_ssps.keys():
            for dex_file in apk_zip.namelist():
                
                if dex_file.endswith('.dex') and dex_file.startswith('class'):
                    print(dex_file)
                    with apk_zip.open(dex_file) as dex_file_content:
                        dex_content = dex_file_content.read()
                        new_size = get_class_size_from_dex(dex_content, target_ssp)
                        target_ssps[target_ssp] = target_ssps[target_ssp] + (new_size / (1024 * 1024))  
    
    print(target_ssps['Lcom/iab/omid/library/vungle'],target_ssps['Lcom/vungle/ads'])

    # Inmobi 
    inmobi_value = target_ssps.get('Lcom/inmobi', 0)
    target_ssps['Inmobi'] = inmobi_value
    target_ssps.pop('Lcom/inmobi', None)

    # Adster
    adster_value = target_ssps.get('Lcom/adster', 0)
    target_ssps['Adster'] = adster_value
    target_ssps.pop('Lcom/adster', None)

    # iron source
    ironsource_value = target_ssps.get('Lcom/ironsource', 0)
    omid_value = target_ssps.get('Lcom/iab/omid/library/ironsrc', 0)
    unity_ads_value = target_ssps.get('Lcom/unity3d/ironsourceads', 0)
    unity_mediation_value = target_ssps.get('Lcom/unity3d/mediation', 0)
    target_ssps['IronSource'] = (
    ironsource_value + omid_value + unity_ads_value + unity_mediation_value
    )
    target_ssps.pop('Lcom/ironsource', None)
    target_ssps.pop('Lcom/iab/omid/library/ironsrc', None)
    target_ssps.pop('Lcom/unity3d/ironsourceads', None)
    target_ssps.pop('Lcom/unity3d/mediation', None)

    # Mintegral 
    mbridge_value = target_ssps.get('Lcom/mbridge/msdk', 0)
    omid_value = target_ssps.get('Lcom/iab/omid/library/mmadbridge', 0)
    target_ssps['Mintegral'] = mbridge_value + omid_value
    target_ssps.pop('Lcom/mbridge/msdk', None)
    target_ssps.pop('Lcom/iab/omid/library/mmadbridge', None)

    # Applovin
    applovin_value = target_ssps.get('Lcom/applovin', 0)
    omid_value = target_ssps.get('Lcom/iab/omid/library/applovin', 0)
    target_ssps['Applovin'] = applovin_value + omid_value
    target_ssps.pop('Lcom/applovin', None)
    target_ssps.pop('Lcom/iab/omid/library/applovin', None)

    # GAM/Admob
    google_gms_value = target_ssps.get('Lcom/google/android/gms', 0)
    target_ssps['GAM/Admob'] = google_gms_value
    target_ssps.pop('Lcom/google/android/gms', None)

    # Unity_clouds 
    ads_value = target_ssps.get('Lcom/unity3d/ads', 0)
    services_value = target_ssps.get('Lcom/unity3d/services', 0)
    omid_value = target_ssps.get('Lcom/iab/omid/library/unity3d', 0)
    scar_v2000_value = target_ssps.get('Lcom/unity3d/scar/adapter/v2000', 0)
    scar_v2100_value = target_ssps.get('Lcom/unity3d/scar/adapter/v2100', 0)
    scar_v2300_value = target_ssps.get('Lcom/unity3d/scar/adapter/v2300', 0)
    scar_common_value = target_ssps.get('Lcom/unity3d/scar/adapter/common', 0)
    target_ssps['Unity_Clouds'] = (
    ads_value + services_value + omid_value +
    scar_v2000_value + scar_v2100_value + scar_v2300_value + scar_common_value
    )
    target_ssps.pop('Lcom/unity3d/ads', None)
    target_ssps.pop('Lcom/unity3d/services', None)
    target_ssps.pop('Lcom/iab/omid/library/unity3d', None)
    target_ssps.pop('Lcom/unity3d/scar/adapter/v2000', None)
    target_ssps.pop('Lcom/unity3d/scar/adapter/v2100', None)
    target_ssps.pop('Lcom/unity3d/scar/adapter/v2300', None)
    target_ssps.pop('Lcom/unity3d/scar/adapter/common', None)

    # facebook 
    facebook_ads_value = target_ssps.get('Lcom/facebook/ads', 0)
    facebook_infer_value = target_ssps.get('Lcom/facebook/infer/annotation', 0)
    target_ssps['facebook'] = facebook_ads_value + facebook_infer_value
    target_ssps.pop('Lcom/facebook/ads', None)
    target_ssps.pop('Lcom/facebook/infer/annotation', None)

    # vungle
    omid_vungle_value = target_ssps.get('Lcom/iab/omid/library/vungle', 0)
    vungle_ads_value = target_ssps.get('Lcom/vungle/ads', 0)
    target_ssps['vungle'] = omid_vungle_value + vungle_ads_value
    target_ssps.pop('Lcom/iab/omid/library/vungle', None)
    target_ssps.pop('Lcom/vungle/ads', None)

    # digital/fiber
    ignite_value = target_ssps.get('Lcom/digitalturbine/ignite', 0)
    inneractive_value = target_ssps.get('Lcom/fyber/inneractive', 0)
    marketplace_value = target_ssps.get('Lcom/fyber/marketplace', 0)
    omid_fyber_value = target_ssps.get('Lcom/iab/omid/library/fyber', 0)
    target_ssps['DigitalTurbine/Fyber'] = (
    ignite_value + inneractive_value + marketplace_value + omid_fyber_value 
    )
    target_ssps.pop('Lcom/digitalturbine/ignite', None)
    target_ssps.pop('Lcom/fyber/inneractive', None)
    target_ssps.pop('Lcom/fyber/marketplace', None)
    target_ssps.pop('Lcom/iab/omid/library/fyber', None)


    ssps = {
        "Lcom/google/ads/mediation/": [],
        "Lcom/applovin/mediation/ads/": [],
        "Lcom/ironsource/adapters/": [],
    }
    
    with ZipFile(file_path, 'r') as apk_zip:
            for ssp in ssps.keys():
                for dex_file in apk_zip.namelist():
                    if dex_file.endswith('.dex') and dex_file.startswith('class'):
                            with apk_zip.open(dex_file) as dex_file_content:
                                dex_content = dex_file_content.read()
                                dex_obj = dvm.DalvikVMFormat(dex_content)
                                for class_obj in dex_obj.get_classes():
                                    if class_obj.get_name().startswith(ssp):
                                        medaited_ssp = class_obj.get_name()[len(ssp):].split("/", 1)[0]
                                        if medaited_ssp not in ssps[ssp] and not medaited_ssp.endswith(';'):
                                            ssps[ssp].append(medaited_ssp)

    return jsonify({
        "message": f"File '{file.filename}' successfully uploaded!",
        "target_ssps": target_ssps,
        "adapters": ssps
    })


@app.route('/findSSP', methods=['GET'])
def findSSP():
    return render_template('findSSP.html')

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=4000, debug=True)
    app.wsgi_app = ProxyFix(app.wsgi_app)  
    run_simple('0.0.0.0', 4000, app, use_reloader=True, threaded=True)
