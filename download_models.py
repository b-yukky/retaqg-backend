import os

weights = {
    "multitask-qg-ag.ckpt": "https://drive.google.com/u/0/uc?id=1-vqF9olcYOT1hk4HgNSYEdRORq-OD5CF&export=download&confirm=t&uuid=25bd5b05-9744-4dd5-af2d-13a5dccea64a&at=ACjLJWkydLJdb3o7p-Sf5HmsGm3y:1671542808588",
    "race-distractors.ckpt": "https://drive.google.com/u/0/uc?id=1jKdcbc_cPkOnjhDoX4jMjljMkboF-5Jv&export=download&confirm=t&uuid=a29f69f8-dfc7-4ec8-9b36-a4c3c61fc277&at=ACjLJWnFGOEt7fU1yuqTsrPwte98:1671587310557"
}

weights_folder = './aqg_api/weights'

def main():
    
    if not os.path.exists(weights_folder):
        os.mkdir(weights_folder)
    
    for model_name, dlink in weights.items():
        save_path = os.path.join(weights_folder, model_name)
        if not os.path.exists(save_path):
            print(f'downloading {model_name} weights...')
            os.system(f'wget -nc "{dlink}" -P {save_path}')
            print(f'download complete.')

if __name__ == "__main__":
    main()
