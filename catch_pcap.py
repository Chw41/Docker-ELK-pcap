import os
import requests
import time

url_template = '{your_pcap_target_url}/pcap/{TeamID}/{}'  # Replace with the actual target URL
headers = {
    'accept': 'application/json',
    # Replace with a valid authorization token if needed
}
save_path = './pcap'

if not os.path.exists(save_path):
    os.makedirs(save_path)

already_downloaded = set(os.listdir(save_path))

for round_number in range(90, 180):
    file_name = f'{round_number}.pcap'
    
    if file_name in already_downloaded:
        continue
    
    url = url_template.format(round_number)
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        with open(os.path.join(save_path, file_name), 'wb') as f:
            f.write(response.content)
        print(f'Catch Round: {round_number} Success')
    else:
        print(f'Round: {round_number} Fail，Status Code：{response.status_code}')
    
    time.sleep(3)
