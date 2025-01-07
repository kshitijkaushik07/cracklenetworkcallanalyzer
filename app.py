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


app = Flask(__name__)

app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = 'uploads'

def har_to_csv():
    # Full path for HAR and CSV files
    har_file_name = 'upload_har.har'
    har_folder = 'har_file_upload'
    csv_folder = 'uploads'
    csv_file_name = 'uploaded_file.csv'
    har_file_path = os.path.join(har_folder, har_file_name)
    csv_file_path = os.path.join(csv_folder, csv_file_name)

    try:
        # Open HAR file and load the data
        with open(har_file_path, "r", encoding="utf-8") as file:
            har_data = json.load(file)

        # Open CSV file for writing
        with open(csv_file_path, "w", newline='', encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write header row for CSV
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

            # Parse the HAR entries and write to CSV
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

    # Path to your uploaded CSV file
    UPLOAD_FOLDER = 'uploads'
    file_name = 'uploaded_file.csv'
    file_path = os.path.join(UPLOAD_FOLDER, file_name)

    # Arrays for 'iu' values
    iu_with_crackle = []
    iu_without_crackle = []

    # If the file exists, proceed with reading and processing the CSV
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
        # Call the function for response body processing
        process_response_body(df, iu_with_crackle, iu_without_crackle)

        # Print results
        print("Aggregated Flags: ")
        for flag, value in aggregated_flags.items():
            print(f"{flag}: {value}")

        print(f"iu values with crackle: {iu_with_crackle}")
        print(f"iu values with no crackle: {iu_without_crackle}")
    else:
        print(f"File '{file_name}' not found in folder '{UPLOAD_FOLDER}'.")

    # Render the results to the template
    return render_template('new_index.html', flags=aggregated_flags,
                           iu_with_crackle=iu_with_crackle, iu_without_crackle=iu_without_crackle)


    
def process_response_body(df, iu_with_crackle, iu_without_crackle):
    # Traverse each row in the DataFrame
    for index, row in df.iterrows():
        request_url = row.get('Request URL', '')
        
        # Proceed only if the 'Request URL' contains the specified expression
        if 'pubads.g.doubleclick.net/gampad/ads' in request_url:
            encoded_response_body = row.get('Response Body', '')
            
            # Fix padding for the base64 string
            missing_padding = len(encoded_response_body) % 4
            if missing_padding != 0:
                encoded_response_body += "=" * (4 - missing_padding)
            
            # Decode the base64 string
            try:
                decoded_bytes = base64.b64decode(encoded_response_body)
                decoded_response_body = decoded_bytes.decode('utf-8')  # Assuming UTF-8 encoded
                
                # Parse the decoded response body as JSON
                response_json = json.loads(decoded_response_body)
                
                # Check if "ad_networks" and "class_name" exist in the JSON
                for ad_network in response_json.get('ad_networks', []):
                    class_name = ad_network.get('data', {}).get('class_name', '').lower()
                    
                    # Extract 'iu' values from the Request URL's query parameters
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

    # Size of the class name
    total_size += len(class_obj.get_name().encode('utf-8'))

    # # Size of the superclass name
    # if class_obj.get_superclassname():
    #     total_size += len(class_obj.get_superclassname().encode('utf-8'))

    # Size of implemented interfaces
    for interface in class_obj.get_interfaces():
        total_size += len(interface.encode('utf-8'))

    # Size of annotations
    # annotations = class_obj.get_annotations()
    # if annotations:
    #     for annotation in annotations:
    #         total_size += len(str(annotation).encode('utf-8'))

    # Size of methods
    for method in class_obj.get_methods():
        if method.get_code():
            total_size += method.get_code().get_length()
        total_size += len(method.get_name().encode('utf-8'))  # Add the size of the method name
        total_size += len(method.get_descriptor().encode('utf-8'))  # Add method descriptor size

    # Size of fields
    for field in class_obj.get_fields():
        total_size += len(field.get_name().encode('utf-8'))
        total_size += len(field.get_descriptor().encode('utf-8'))  # Add field descriptor size

    # Add shared references (strings, constants, etc.)
    # for reference in analysis.get_field_analysis(class_obj):
    #     total_size += len(reference.field.get_name())
    #     total_size += len(reference.field.get_descriptor())

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
    # Check if the 'apkFile' is part of the request
    if 'apkFile' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['apkFile']

    # Check if a file was selected
    if file.filename == '':
        return jsonify({"message": "No file selected for uploading"}), 400

    # Ensure the file is an APK
    if not file.filename.endswith('.apk'):
        return jsonify({"message": "Invalid file type. Only .apk files are allowed."}), 400

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(file_path)

    target_ssps = {
        'Lcom/google': 0.0,
        'Lcom/applovin': 0.0,
        'Lcom/ironsource':0.0,
        'Lcom/fyber': 0.0,
        'Lcom/facebook':0.0,
        'Lcom/adinmo':0.0,
        'Lcom/admofi':0.0,
        'Lcom/unity':0.0,
        'Lcom/gadsme':0.0,
        'Lcom/admob':0.0,
        'Lcom/inmobi':0.0,
        'Lcom/vungle':0.0,
        'Lcom/adster':0.0,
        'Lcom/flury':0.0,
    }

    # with ZipFile(file_path, 'r') as apk_zip:
    #     for target_ssp in target_ssps.keys():
    #         for dex_file in apk_zip.namelist():
    #             if dex_file.endswith('.dex') and dex_file.startswith('class'):
    #                 with apk_zip.open(dex_file) as dex_file_content:
    #                     dex_content = dex_file_content.read()
    #                     new_size = get_class_size_from_dex(dex_content, target_ssp)
    #                     target_ssps[target_ssp] = target_ssps[target_ssp] + (new_size / (1024 * 1024))  

    ssps = {
        "Lcom/google/ads/mediation/": [],
        "Lcom/applovin/": [],
        "Lcom/ironsource/": [],
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
                                    if medaited_ssp not in ssps[ssp]:
                                        ssps[ssp].append(medaited_ssp)

    print(ssps)

    return jsonify({
        "message": f"File '{file.filename}' successfully uploaded!",
        "target_ssps": target_ssps,
        "adapters": []
    })


@app.route('/findSSP', methods=['GET'])
def findSSP():
    return render_template('findSSP.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
