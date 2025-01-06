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


def get_classes_from_dex(dex_content):
    """
    Extract class names from a dex file content using androguard.
    """
    try:
        dvm = DalvikVMFormat(dex_content)
        classes = [cls.get_name() for cls in dvm.get_classes()]
        return classes
    except Exception as e:
        return [f"Error parsing dex: {str(e)}"]
    

def get_class_size_and_inheritances(class_obj, visited_classes):
    """
    Recursively calculate the size of a class and its inherited components.
    """
    if class_obj.get_name() in visited_classes:
        return 0  # Prevent infinite recursion for circular inheritance

    # Mark this class as visited
    visited_classes.add(class_obj.get_name())
    
    class_size = 0

    # Calculate size of methods in this class
    for method in class_obj.get_methods():
        class_size += len(method.get_name()) + method.get_code().get_length()

    # Calculate size of fields in this class
    for field in class_obj.get_fields():
        class_size += len(field.get_name())

    # Recursively calculate the size of inherited classes (parent class)
    parent_class_name = class_obj.get_superclass_name()
    if parent_class_name and parent_class_name != "Ljava/lang/Object;":
        # Get the parent class object and calculate its size
        parent_class = class_obj.get_vm().get_class_by_name(parent_class_name)
        if parent_class:
            class_size += get_class_size_and_inheritances(parent_class, visited_classes)

    return class_size

def calculate_class_size(class_obj):
    """
    Calculate the total size of a class including methods, fields, and metadata.
    """
    total_size = 0

    # Size of the class name
    total_size += len(class_obj.get_name())

    # Size of the superclass name
    if class_obj.get_superclassname():
        total_size += len(class_obj.get_superclassname())

    # Size of implemented interfaces
    for interface in class_obj.get_interfaces():
        total_size += len(interface)

    # Size of methods
    for method in class_obj.get_methods():
        if method.get_code():  # Some methods may not have code (e.g., abstract methods)
            total_size += method.get_code().get_length()
        total_size += len(method.get_name())  # Add the size of the method name

    # Size of fields
    for field in class_obj.get_fields():
        total_size += len(field.get_name())
        total_size += len(field.get_descriptor())  # Add field descriptor size

    return total_size

def get_class_size_from_dex(dex_content, target_class_name='Lcom/'):
    dex_obj = dvm.DalvikVMFormat(dex_content)
    total_size = 0
    for class_obj in dex_obj.get_classes():
        if class_obj.get_name().startswith(target_class_name):
            print("hi")
            print(class_obj.get_name())
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

    target_class_name = "Lcom"  # Replace with your class name

    with ZipFile(file_path, 'r') as apk_zip:
        for dex_file in apk_zip.namelist():
            if dex_file.endswith('.dex'):
                with apk_zip.open(dex_file) as dex_file_content:
                    dex_content = dex_file_content.read()
                    if dex_file == "classes.dex":
                        class_size = get_class_size_from_dex(dex_content)
                    if class_size:
                        print(f"Total size of {target_class_name}: {class_size / (1024 * 1024)} MB")

    # try:
    #     dex_files = []
    #     folder_sizes = defaultdict(int)
        
        # # Extract the contents of the APK
        # with ZipFile(file_path, 'r') as apk_zip:
        #     file_list = apk_zip.namelist()
        #     dex_files = [file for file in file_list if file.startswith('classes') and file.endswith('.dex')]
            
            # visited_classes = set()  # To track visited classes and avoid circular inheritance
            # # Iterate through all dex files
            # for dex_file in dex_files:
            #     with apk_zip.open(dex_file) as dex_file_content:
            #         # Using Androguard to parse dex file content
            #         dex_content = dex_file_content.read()
            #         # Load the APK
            #         # apk_obj = apk.APK(None)
            #         dex_obj = dvm.DalvikVMFormat(dex_content)
                    
            #         # Extract classes from dex file
            #         for class_obj in dex_obj.get_classes():
            #             # Get class name and calculate its size
            #             class_name = class_obj.get_name()
            #             folder_path = "/".join(class_name.split('/')[:2])  # Get folder structure like Lcom/google
            #             print("nijnjn"+class_name)
            #             # Only consider subfolders of "Lcom/google"
            #             if folder_path.startswith("Lcom/applovin/"):
            #                 print("flsnf")
            #                 subfolder_path = "/".join(class_name.split('/')[:3])  # e.g., Lcom/google/foo
                            
            #                 # Calculate total size for class and its inherited components
            #                 class_size = get_class_size_and_inheritances(class_obj, visited_classes)
                            
            #                 # Convert size to MB (can use KB if needed)
            #                 class_size_in_mb = class_size / (1024 * 1024)  # Convert bytes to MB
                            
            #                 # Increment size for the folder (subfolder)
            #                 folder_sizes[subfolder_path] += class_size_in_mb


    # try:
    #     dex_files = []
    #     folder_sizes = defaultdict(int)
    #     # Extract the contents of the APK
    #     with ZipFile(file_path, 'r') as apk_zip:
    #         file_list = apk_zip.namelist()
    #         dex_files = [file for file in file_list if file.startswith('classes') and file.endswith('.dex')]
    #         # for dex_file in dex_files[0]:
    #         dex_file = dex_files[0]
    #         with apk_zip.open(dex_file) as dex_file_content:
    #             dex_content = dex_file_content.read()
    #             dex_obj = dvm.DalvikVMFormat(dex_content)
    #             # dex_classes = get_classes_from_dex(dex_file_content.read())
    #             for class_obj in dex_obj.get_classes():
    #                 # Get class name and calculate its size
    #                     class_name = class_obj.get_name()
    #                     folder_path = "/".join(class_name.split('/')[:2])  # Get folder structure like Lcom/google
                        
    #                     # Only consider subfolders of "Lcom/google"
    #                     subfolder_path = "/".join(class_name.split('/')[:3])  # e.g., Lcom/google/foo
                        
    #                     # Calculate size based on the class's methods, fields, etc.
    #                     class_size = 0
    #                     for method in class_obj.get_methods():
    #                         # Adding method size (method name length + code size)
    #                         class_size += len(method.get_name()) + method.get_code().get_length()
                        
    #                     for field in class_obj.get_fields():
    #                         # Adding field size (field name length)
    #                         class_size += len(field.get_name())
                        
    #                     # Convert size to MB (can use KB if needed)
    #                     class_size_in_mb = class_size / (1024 * 1024)  # Convert bytes to MB
                        
    #                     # Increment size for the folder (subfolder)
    #                     folder_sizes[subfolder_path] += class_size_in_mb


        # print(folder_sizes)
        # print(len(folder_sizes))
        # folder_sizes_dict = dict(folder_sizes)  # Convert defaultdict to dict
        # print(json.dumps(folder_sizes_dict, indent=4))

        return jsonify({
            "message": f"File '{file.filename}' successfully uploaded!",
            "included_files": ""
        })
    # except Exception as e:
    #     return jsonify({"message": f"An error occurred while processing the APK: {str(e)}"}), 500

@app.route('/findSSP', methods=['GET'])
def findSSP():
    return render_template('findSSP.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)