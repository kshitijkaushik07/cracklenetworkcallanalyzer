from flask import Flask, jsonify, render_template, request
import os
from numpy import true_divide
import pandas as pd
import csv
import base64
import json
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

app.secret_key = 'your_secret_key'

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


@app.route('/hi', methods=['GET'])
def hi():
    return jsonify({"user": "garvit"})


@app.route('/findSSP', methods=['GET'])
def findSSP():
    return render_template('findSSP.html')

@app.route('/upload', methods=['POST'])
def upload_apk():
    if 'apkFile' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['apkFile']

    if file.filename == '':
        return jsonify({"message": "No file selected for uploading"}), 400

    if not file.filename.endswith('.apk'):
        return jsonify({"message": "Invalid file type. Only .apk files are allowed."}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    return jsonify({"message": f"File '{file.filename}' successfully uploaded!"})

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=4000, debug=True)