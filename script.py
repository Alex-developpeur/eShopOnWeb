import yaml
import json

def read_yaml(yaml_file):
    data = []
    try:
        with open(yaml_file, 'r') as f:
            yaml_file = yaml.load(f, Loader=yaml.SafeLoader)
            
        # Print the values as a dictionary
        paths = yaml_file['paths']
        collection = None
        for path in paths:
            verbs = paths[path].keys()
            for verb in verbs:
                if (verb == 'get' or verb == 'post') and collection != paths[path][verb]['tags'][0]:
                    collection = paths[path][verb]['tags'][0]
                    data.append({
                                    "name": collection,
                                    "item": []
                                })
                if (verb == 'get' or verb == 'post'):
                    endpoint = create_endpoint_call(paths, path, verb)
                    data[-1]['item'].append(endpoint)
                    print(path)
    #        print(data)
    except Exception as e:
        print(f'Error occurred when opening {yaml_file} to read: {e}')
        return None

    return data

def create_endpoint_call(paths, path, verb):
    ulr_path = path.replace('{', '{{').replace('}', '}}')
    endpoint = {
        "name": paths[path][verb]['summary'],
        "event": [],
        "request":
        {
            "method": verb.upper(),
            "header": [],
            "url": {
                "raw": "https://{{CORE_URI}}" + ulr_path,
                "protocol": "https",
                "host": [
                    "{{CORE_URI}}"
                ],
                "path": [
                    ulr_path[1:]
                ]
            }
        },
        "response": []
    }
    if verb == 'post':
        if 'requestBody' not in paths[path]['post']:
            add_post_body(endpoint, "urlencoded", None)
        elif 'multipart/form-data' in paths[path]['post']['requestBody']['content']:
            properties = paths[path]['post']['requestBody']['content']['multipart/form-data']['schema']['properties']
            add_post_body(endpoint, "formdata", properties)
        elif 'allOf' not in paths[path]['post']['requestBody']['content']['application/x-www-form-urlencoded']['schema']:
            properties = paths[path]['post']['requestBody']['content']['application/x-www-form-urlencoded']['schema']['properties']
            add_post_body(endpoint, "urlencoded", properties)
        else:
            for element in paths[path]['post']['requestBody']['content']['application/x-www-form-urlencoded']['schema']['allOf']:
                if 'properties' in element:
                    add_post_body(endpoint, "urlencoded", element['properties'])
    return endpoint

def add_post_body(endpoint, form_body, properties):
    endpoint['request']['body'] = {
        "mode": form_body,
        form_body: []
    }
    if properties != None:
        for propertie in properties:
            if 'description' in properties[propertie]:
                description = properties[propertie]['description'].replace("<br/>", "\n").replace("</br>", "\n")
                description = description.replace(" <ul> <li>", "").replace("</li> </ul>", "")
                description = description.replace(" <li>", "").replace("</li>", "\n")
                description = description.strip()
            endpoint['request']['body'][form_body].append({
                "key": propertie,
                "value": "",
                "description": description,
                "type": "text"
            })

def write_json(open_api, json_file):
    # Open and read the JSON file
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except Exception as e:
        print(f'Error occurred when opening {json_file} to read: {e}')
        return None

    # Print the data
#    print(data)
    data['item'] = open_api

    json_object = json.dumps(data, indent=4)
    try:
        with open('api-core-script-test.postman_collection.json', 'w') as outfile:
            try:
                outfile.write(json_object)
            except (IOError, OSError):
                print('Error writing to file')
    except (PermissionError, OSError):
        print('Error opening file')

def main():
    print("[START]")
    yaml_file = 'openapi.yaml'
    data = read_yaml(yaml_file)
    json_file = 'folder.postman_collection.json'
    write_json(data, json_file)
    print("[END]")

if __name__ == "__main__":
    main()