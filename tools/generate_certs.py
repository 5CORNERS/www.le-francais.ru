import os
import certifi

def generate_combined_ca():
    certs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tinkoff_merchant', 'certs'))
    if not os.path.exists(certs_dir):
        return
    f_out = os.path.join(certs_dir, 'combined_ca.pem')
    default_certs = open(certifi.where(), 'r', encoding='utf-8').read()
    custom_certs = []
    for f in os.listdir(certs_dir):
        if (f.endswith('.pem') or f.endswith('.crt')) and f != 'combined_ca.pem':
            with open(os.path.join(certs_dir, f), 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                if '-----BEGIN CERTIFICATE-----' in content:
                    custom_certs.append(content.strip())
    with open(f_out, 'w', encoding='utf-8') as out:
        out.write(default_certs + '\n\n' + '\n\n'.join(custom_certs) + '\n')
    print('Generated combined CA bundle at:', f_out)

if __name__ == '__main__':
    generate_combined_ca()
